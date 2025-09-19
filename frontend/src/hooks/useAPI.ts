/**
 * React Query hooks for Wall-E Research API integration
 * Provides data fetching, caching, and real-time updates
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, type MetricsSummary, type Product, type ScraperStatus, type LogEntry, type ConfigValues, type AutoDetectionStatus } from '@/services/api';
import { toast } from '@/hooks/use-toast';

// Query Keys for React Query
export const queryKeys = {
  metrics: ['metrics', 'summary'] as const,
  products: ['products'] as const,
  productStats: ['products', 'stats'] as const,
  scrapers: ['scrapers', 'status'] as const,
  logs: (limit?: number, level?: string, source?: string) => ['logs', 'recent', { limit, level, source }] as const,
  config: ['config', 'current'] as const,
  autoDetection: {
    status: ['auto-detection', 'status'] as const,
    config: ['auto-detection', 'config'] as const,
    statistics: ['auto-detection', 'statistics'] as const,
    detectedProducts: ['auto-detection', 'detected-products'] as const,
  },
  aiEngine: ['ai-engine', 'stats'] as const,
  health: ['health'] as const,
};

// Metrics Hooks
export const useMetrics = () => {
  return useQuery({
    queryKey: queryKeys.metrics,
    queryFn: api.getMetricsSummary,
    refetchInterval: 5000, // Refresh every 5 seconds
    staleTime: 2000, // Consider data stale after 2 seconds
  });
};

// Products Hooks
export const useProducts = () => {
  return useQuery({
    queryKey: queryKeys.products,
    queryFn: api.getProducts,
    refetchInterval: 10000, // Refresh every 10 seconds
    staleTime: 0, // Consider data stale immediately
    cacheTime: 0, // Don't cache data (for debugging)
  });
};

export const useProductStats = () => {
  return useQuery({
    queryKey: queryKeys.productStats,
    queryFn: api.getProductStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

export const useAddProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.addProduct,
    onSuccess: (newProduct) => {
      // Update products list
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
      queryClient.invalidateQueries({ queryKey: queryKeys.productStats });
      
      toast({
        title: "Producto agregado",
        description: `${newProduct.title} ha sido agregado correctamente.`,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al agregar producto",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

export const useUpdateProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ productId, updates }: { productId: string; updates: Record<string, unknown> }) =>
      api.updateProduct(productId, updates),
    onSuccess: (updatedProduct) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
      queryClient.invalidateQueries({ queryKey: queryKeys.productStats });
      
      toast({
        title: "Producto actualizado",
        description: `${updatedProduct.title} ha sido actualizado.`,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al actualizar producto",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

export const useDeleteProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.deleteProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
      queryClient.invalidateQueries({ queryKey: queryKeys.productStats });
      
      toast({
        title: "Producto eliminado",
        description: "El producto ha sido eliminado correctamente.",
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al eliminar producto",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

// Scrapers Hooks
export const useScrapers = () => {
  return useQuery({
    queryKey: queryKeys.scrapers,
    queryFn: api.getScraperStatus,
    refetchInterval: 8000, // Refresh every 8 seconds
  });
};

// Logs Hooks
export const useLogs = (limit = 50, level?: string, source?: string) => {
  return useQuery({
    queryKey: queryKeys.logs(limit, level, source),
    queryFn: () => api.getRecentLogs(limit, level, source),
    refetchInterval: 3000, // Refresh every 3 seconds
  });
};

// Configuration Hooks
export const useConfig = () => {
  return useQuery({
    queryKey: queryKeys.config,
    queryFn: api.getCurrentConfig,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

export const useUpdateConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ key, value, applyImmediately = true }: { key: string; value: string | number | boolean; applyImmediately?: boolean }) =>
      api.updateConfig(key, value, applyImmediately),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.config });
      
      toast({
        title: "Configuración actualizada",
        description: result.message,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al actualizar configuración",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

// Auto-Detection Hooks
export const useAutoDetectionStatus = () => {
  return useQuery({
    queryKey: queryKeys.autoDetection.status,
    queryFn: api.getAutoDetectionStatus,
    refetchInterval: 5000, // Refresh every 5 seconds
  });
};

export const useAutoDetectionConfig = () => {
  return useQuery({
    queryKey: queryKeys.autoDetection.config,
    queryFn: api.getAutoDetectionConfig,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

export const useAutoDetectionStatistics = () => {
  return useQuery({
    queryKey: queryKeys.autoDetection.statistics,
    queryFn: api.getAutoDetectionStatistics,
    refetchInterval: 15000, // Refresh every 15 seconds
  });
};

export const useDetectedProducts = () => {
  return useQuery({
    queryKey: queryKeys.autoDetection.detectedProducts,
    queryFn: api.getDetectedProducts,
    refetchInterval: 10000, // Refresh every 10 seconds
  });
};

export const useStartAutoDetection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.startAutoDetection,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.autoDetection.status });
      
      toast({
        title: "Auto-detección iniciada",
        description: result.message,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al iniciar auto-detección",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

export const useStopAutoDetection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.stopAutoDetection,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.autoDetection.status });
      
      toast({
        title: "Auto-detección detenida",
        description: result.message,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al detener auto-detección",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

export const useManualScan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.manualScan,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.autoDetection.detectedProducts });
      queryClient.invalidateQueries({ queryKey: queryKeys.products });
      
      toast({
        title: "Escaneo manual completado",
        description: `Encontrados ${result.products_found} productos, ${result.new_products} nuevos.`,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error en escaneo manual",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

export const useUpdateAutoDetectionConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.updateAutoDetectionConfig,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.autoDetection.config });
      queryClient.invalidateQueries({ queryKey: queryKeys.autoDetection.status });
      
      toast({
        title: "Configuración de auto-detección actualizada",
        description: result.message,
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Error al actualizar configuración",
        description: error instanceof Error ? error.message : "Error desconocido",
      });
    },
  });
};

// AI Engine Hooks
export const useAIEngineStats = () => {
  return useQuery({
    queryKey: queryKeys.aiEngine,
    queryFn: api.getAIEngineStats,
    refetchInterval: 10000, // Refresh every 10 seconds
  });
};

// Health Check Hook
export const useHealth = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: api.healthCheck,
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: 3,
  });
};