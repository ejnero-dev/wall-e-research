/**
 * API Service for Wall-E Research Backend Integration
 * Connects with FastAPI backend at localhost:8000/api/dashboard
 */

const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000/api/dashboard'
  : 'http://localhost:8000/api/dashboard';

// Types for API responses
export interface MetricsSummary {
  msg_rate: number;
  active_scrapers: number;
  success_rate: number;
  avg_response_time: number;
  total_messages_today: number;
  total_errors_today: number;
  timestamp: string;
}

export interface Product {
  id: string;
  title: string;
  description: string;
  price: number;
  original_price?: number;
  sku?: string;
  category: string;
  condition: string;
  status: string;
  wallapop_url: string;
  image_url?: string;
  images?: string[];
  views: number;
  messages_received: number;
  last_activity?: string;
  created_at: string;
  updated_at: string;
  auto_respond: boolean;
  ai_personality?: string;
  response_delay_min?: number;
  response_delay_max?: number;
  location?: string;
  shipping_available: boolean;
  shipping_cost?: number;
  conversion_rate?: number;
  avg_response_time?: number;
  fraud_attempts: number;
  successful_sales: number;
}

export interface ScraperStatus {
  scraper_id: string;
  status: string;
  last_activity: string;
  messages_processed: number;
  uptime_seconds: number;
  current_task?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  message: string;
  source: string;
  metadata?: Record<string, unknown>;
}

export interface AutoDetectionStatus {
  status: string;
  is_running: boolean;
  last_scan?: string;
  products_detected?: number;
  total_products_managed?: number;
}

export interface ConfigValues {
  msg_per_hour: number;
  retry_attempts: number;
  timeout: number;
  rate_limit: number;
  debug_mode: boolean;
  auto_response: boolean;
}

export interface AutoDetectionConfig {
  enabled: boolean;
  search_keywords: string[];
  price_range_min: number;
  price_range_max: number;
  categories: string[];
  auto_respond_new_products: boolean;
  ai_personality: string;
  response_delay_min: number;
  response_delay_max: number;
  enable_notifications: boolean;
}

export interface DetectedProduct {
  id: string;
  title: string;
  price: number;
  url: string;
  image_url?: string;
  detected_at: string;
  status: string;
  category?: string;
  description?: string;
}

export interface AutoDetectionStatistics {
  total_searches: number;
  products_found: number;
  products_added: number;
  last_search_time?: string;
  success_rate: number;
}

// API Error class
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

// Generic fetch wrapper with error handling
async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// API Methods
export const api = {
  // Metrics
  getMetricsSummary: (): Promise<MetricsSummary> =>
    fetchAPI<MetricsSummary>('/metrics/summary'),

  // Products
  getProducts: (): Promise<Product[]> =>
    fetchAPI<Product[]>('/products'),

  addProduct: (productData: { wallapop_url: string; auto_respond?: boolean; ai_personality?: string; response_delay_min?: number; response_delay_max?: number }) =>
    fetchAPI<Product>('/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    }),

  updateProduct: (productId: string, updates: Partial<Product>) =>
    fetchAPI<Product>(`/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),

  deleteProduct: (productId: string) =>
    fetchAPI<{ message: string }>(`/products/${productId}`, {
      method: 'DELETE',
    }),

  getProductStats: () =>
    fetchAPI<{
      total: number;
      active: number;
      paused: number;
      sold: number;
      total_views: number;
      total_messages: number;
      conversion_rate: number;
      revenue_this_month: number;
    }>('/products/stats'),

  // Scrapers
  getScraperStatus: (): Promise<ScraperStatus[]> =>
    fetchAPI<ScraperStatus[]>('/scraper/status'),

  // Logs
  getRecentLogs: (limit = 50, level?: string, source?: string): Promise<LogEntry[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (level) params.append('level', level);
    if (source) params.append('source', source);
    return fetchAPI<LogEntry[]>(`/logs/recent?${params}`);
  },

  // Configuration
  getCurrentConfig: (): Promise<ConfigValues> =>
    fetchAPI<ConfigValues>('/config/current'),

  updateConfig: (key: string, value: string | number | boolean, applyImmediately = true) =>
    fetchAPI<{ status: string; message: string; applied: boolean }>('/config/update', {
      method: 'POST',
      body: JSON.stringify({
        key,
        value,
        apply_immediately: applyImmediately,
      }),
    }),

  // Auto-Detection
  getAutoDetectionStatus: (): Promise<AutoDetectionStatus> =>
    fetchAPI<AutoDetectionStatus>('/auto-detection/status'),

  startAutoDetection: () =>
    fetchAPI<{ status: string; message: string; timestamp: string }>('/auto-detection/start', {
      method: 'POST',
    }),

  stopAutoDetection: () =>
    fetchAPI<{ status: string; message: string; timestamp: string }>('/auto-detection/stop', {
      method: 'POST',
    }),

  manualScan: () =>
    fetchAPI<{ products_found: number; new_products: number; updated_products: number }>('/auto-detection/scan', {
      method: 'POST',
    }),

  getAutoDetectionConfig: () =>
    fetchAPI<{
      enabled: boolean;
      scan_interval_minutes: number;
      auto_add_products: boolean;
      auto_respond_new_products: boolean;
      ai_personality: string;
      response_delay_min: number;
      response_delay_max: number;
      enable_notifications: boolean;
    }>('/auto-detection/config'),

  updateAutoDetectionConfig: (config: Partial<AutoDetectionConfig>) =>
    fetchAPI<{ status: string; message: string; config: AutoDetectionConfig }>('/auto-detection/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    }),

  getAutoDetectionStatistics: () =>
    fetchAPI<{
      available: boolean;
      statistics?: AutoDetectionStatistics;
      error?: string;
      timestamp: string;
    }>('/auto-detection/statistics'),

  getDetectedProducts: () =>
    fetchAPI<DetectedProduct[]>('/auto-detection/detected-products'),

  // AI Engine
  getAIEngineStats: () =>
    fetchAPI<{
      status: string;
      engine_status: string;
      uptime_seconds: number;
      total_requests: number;
      success_rate: number;
      ai_response_rate: number;
      average_response_time: number;
      requests_per_second: number;
      error?: string;
    }>('/ai-engine/stats'),

  // Health Check
  healthCheck: () =>
    fetchAPI<{
      status: string;
      timestamp: string;
      services: {
        api: string;
        redis: string;
        websocket: {
          status: string;
          active_connections: number;
        };
      };
    }>('/health'),
};

export default api;