/**
 * WebSocket hook for real-time data updates
 * Connects to Wall-E Research backend WebSocket endpoint
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './useAPI';
import { toast } from './use-toast';
import type { LogEntry, ScraperStatus } from '@/services/api';

interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp?: string;
}

interface UseWebSocketOptions {
  url?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
}

interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  reconnectCount: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    url = process.env.NODE_ENV === 'development' 
      ? 'ws://localhost:8000/api/dashboard/ws/live'
      : 'ws://localhost:8000/api/dashboard/ws/live',
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    reconnectCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const queryClient = useQueryClient();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();

  // Send message to server
  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Handle incoming messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Handle different message types
      switch (message.type) {
        case 'initial':
          // Handle initial data load
          if (message.data.metrics) {
            queryClient.setQueryData(queryKeys.metrics, message.data.metrics);
          }
          if (message.data.logs) {
            queryClient.setQueryData(queryKeys.logs(10), message.data.logs);
          }
          break;

        case 'metrics_update':
          // Update metrics data
          queryClient.setQueryData(queryKeys.metrics, message.data);
          break;

        case 'new_log':
          // Add new log entry
          queryClient.setQueryData(queryKeys.logs(50), (oldData: LogEntry[] | undefined) => {
            if (!oldData) return [message.data as LogEntry];
            return [message.data as LogEntry, ...oldData].slice(0, 50);
          });
          break;

        case 'scraper_update':
          // Update scraper status
          queryClient.setQueryData(queryKeys.scrapers, (oldData: ScraperStatus[] | undefined) => {
            if (!oldData) return [];
            const updateData = message.data as Partial<ScraperStatus> & { scraper_id: string };
            return oldData.map(scraper =>
              scraper.scraper_id === updateData.scraper_id
                ? { ...scraper, ...updateData }
                : scraper
            );
          });
          break;

        case 'product_added':
          // Invalidate product queries to refresh
          queryClient.invalidateQueries({ queryKey: queryKeys.products });
          queryClient.invalidateQueries({ queryKey: queryKeys.productStats });
          
          if (message.data.source === 'auto-detection') {
            toast({
              title: "Nuevo producto detectado",
              description: `${message.data.product.title} ha sido agregado automáticamente.`,
            });
          }
          break;

        case 'product_updated':
          // Update specific product
          queryClient.invalidateQueries({ queryKey: queryKeys.products });
          break;

        case 'config_update':
          // Refresh config data
          queryClient.invalidateQueries({ queryKey: queryKeys.config });
          break;

        case 'heartbeat':
          // Respond to server heartbeat
          sendMessage({ type: 'pong', timestamp: new Date().toISOString() });
          break;

        case 'pong':
          // Server responded to our ping
          break;

        default:
          console.log('Unknown WebSocket message type:', message.type);
      }

      // Call custom message handler
      if (onMessage) {
        onMessage(message);
      }

    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }, [queryClient, onMessage, sendMessage]);

  // Setup heartbeat mechanism
  const setupHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendMessage({ type: 'ping', timestamp: new Date().toISOString() });
      }
    }, 30000); // Ping every 30 seconds
  }, [sendMessage]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.CONNECTING || state.isConnecting) {
      return; // Already connecting
    }

    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          reconnectCount: 0,
          error: null,
        }));

        setupHeartbeat();
        
        if (onConnect) {
          onConnect();
        }

        console.log('WebSocket connected to:', url);
      };

      ws.onmessage = handleMessage;

      ws.onclose = (event) => {
        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));

        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        if (onDisconnect) {
          onDisconnect();
        }

        // Attempt to reconnect if not a manual close
        if (event.code !== 1000 && state.reconnectCount < maxReconnectAttempts) {
          setState(prev => ({ ...prev, reconnectCount: prev.reconnectCount + 1 }));
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting WebSocket reconnection (${state.reconnectCount + 1}/${maxReconnectAttempts})`);
            connect();
          }, reconnectInterval);
        } else if (state.reconnectCount >= maxReconnectAttempts) {
          setState(prev => ({
            ...prev,
            error: 'Max reconnection attempts reached',
          }));
        }

        console.log('WebSocket disconnected');
      };

      ws.onerror = (error) => {
        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
          error: 'Connection error',
        }));

        if (onError) {
          onError(error);
        }

        console.error('WebSocket error:', error);
      };

    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }, [url, handleMessage, state.reconnectCount, state.isConnecting, maxReconnectAttempts, reconnectInterval, setupHeartbeat, onConnect, onDisconnect, onError]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      reconnectCount: 0,
    });
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect]); // Only depend on autoConnect to avoid reconnecting on every change

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage,
  };
};

// Hook for easy integration into components
export const useRealtimeUpdates = () => {
  const webSocket = useWebSocket({
    onConnect: () => {
      console.log('Real-time updates connected');
    },
    onDisconnect: () => {
      console.log('Real-time updates disconnected');
    },
    onError: (error) => {
      console.error('Real-time updates error:', error);
      toast({
        variant: "destructive",
        title: "Conexión perdida",
        description: "Intentando reconectar...",
      });
    },
  });

  return webSocket;
};

export default useWebSocket;