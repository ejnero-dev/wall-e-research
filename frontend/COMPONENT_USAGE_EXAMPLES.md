# Component Usage Examples

This document provides examples of how to use the AdvancedMetrics and NotificationCenter components in the Wall-E Research dashboard.

## AdvancedMetrics Component

### Basic Usage

```tsx
import { AdvancedMetrics } from '@/components/AdvancedMetrics';

function Dashboard() {
  return (
    <div className="space-y-4">
      <AdvancedMetrics />
    </div>
  );
}
```

### With Custom Data

```tsx
import { AdvancedMetrics } from '@/components/AdvancedMetrics';

function Dashboard() {
  const metricsData = {
    sales: {
      total: 45230,
      today: 1250,
      thisWeek: 8900,
      thisMonth: 24500,
      target: 30000,
      averageValue: 125,
      conversionRate: 12.5,
    },
    messages: {
      total: 5420,
      messagesPerHour: 8.5,
      responseTime: 3.2,
      automatedResponses: 4850,
      pendingMessages: 12,
    },
    automation: {
      activeScrapers: 5,
      successRate: 94.2,
      uptime: 99.8,
      tasksCompleted: 15420,
      errorCount: 3,
    },
    users: {
      totalUsers: 2340,
      activeUsers: 856,
      newUsers: 47,
      engagementRate: 68.5,
    },
  };

  return (
    <div className="space-y-4">
      <AdvancedMetrics data={metricsData} />
    </div>
  );
}
```

### With Loading State

```tsx
import { AdvancedMetrics } from '@/components/AdvancedMetrics';
import { useMetrics } from '@/hooks/useAPI';

function Dashboard() {
  const { data: apiMetrics, isLoading } = useMetrics();

  return (
    <div className="space-y-4">
      <AdvancedMetrics
        data={apiMetrics}
        isLoading={isLoading}
      />
    </div>
  );
}
```

### TypeScript Interface

```tsx
export interface AdvancedMetricsProps {
  data?: {
    sales?: SalesMetrics;
    messages?: MessagesMetrics;
    automation?: AutomationMetrics;
    users?: UsersMetrics;
  };
  isLoading?: boolean;
}

interface SalesMetrics {
  total: number;
  today: number;
  thisWeek: number;
  thisMonth: number;
  target: number;
  averageValue: number;
  conversionRate: number;
}

interface MessagesMetrics {
  total: number;
  messagesPerHour: number;
  responseTime: number;
  automatedResponses: number;
  pendingMessages: number;
}

interface AutomationMetrics {
  activeScrapers: number;
  successRate: number;
  uptime: number;
  tasksCompleted: number;
  errorCount: number;
}

interface UsersMetrics {
  totalUsers: number;
  activeUsers: number;
  newUsers: number;
  engagementRate: number;
}
```

## NotificationCenter Component

### Basic Usage (Bell Icon with Badge)

```tsx
import { NotificationCenter } from '@/components/NotificationCenter';

function AppHeader() {
  return (
    <header className="flex items-center justify-between p-4">
      <h1>Wall-E Dashboard</h1>
      <div className="flex items-center gap-4">
        <NotificationCenter />
      </div>
    </header>
  );
}
```

### With Custom Notifications

```tsx
import { NotificationCenter, Notification } from '@/components/NotificationCenter';
import { useState } from 'react';

function AppHeader() {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      type: 'warning',
      priority: 'high',
      title: 'Posible fraude detectado',
      message: 'Se ha detectado un intento de fraude en la conversacion con @usuario123',
      timestamp: new Date().toISOString(),
      read: false,
    },
    {
      id: '2',
      type: 'success',
      priority: 'medium',
      title: 'Venta completada',
      message: 'Producto iPhone 12 Pro vendido por 450€',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      read: false,
    },
    {
      id: '3',
      type: 'product',
      priority: 'low',
      title: 'Nuevo producto detectado',
      message: 'Se encontro un producto que coincide con tus criterios',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      read: true,
    },
  ]);

  const handleMarkAsRead = (notificationId: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleClearAll = () => {
    setNotifications([]);
  };

  const handleNotificationClick = (notification: Notification) => {
    console.log('Notification clicked:', notification);
    // Navigate to relevant page or show details
  };

  return (
    <header className="flex items-center justify-between p-4">
      <h1>Wall-E Dashboard</h1>
      <div className="flex items-center gap-4">
        <NotificationCenter
          notifications={notifications}
          onMarkAsRead={handleMarkAsRead}
          onMarkAllAsRead={handleMarkAllAsRead}
          onClearAll={handleClearAll}
          onNotificationClick={handleNotificationClick}
          maxDisplay={50}
        />
      </div>
    </header>
  );
}
```

### With API Integration

```tsx
import { NotificationCenter, Notification } from '@/components/NotificationCenter';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function AppHeader() {
  const queryClient = useQueryClient();

  // Fetch notifications from API
  const { data: notifications = [] } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await fetch('/api/dashboard/notifications');
      return response.json();
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: string) => {
      await fetch(`/api/dashboard/notifications/${notificationId}/read`, {
        method: 'POST',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      await fetch('/api/dashboard/notifications/mark-all-read', {
        method: 'POST',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  // Clear all mutation
  const clearAllMutation = useMutation({
    mutationFn: async () => {
      await fetch('/api/dashboard/notifications/clear', {
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  return (
    <header className="flex items-center justify-between p-4">
      <h1>Wall-E Dashboard</h1>
      <div className="flex items-center gap-4">
        <NotificationCenter
          notifications={notifications}
          onMarkAsRead={(id) => markAsReadMutation.mutate(id)}
          onMarkAllAsRead={() => markAllAsReadMutation.mutate()}
          onClearAll={() => clearAllMutation.mutate()}
          onNotificationClick={(notification) => {
            // Handle navigation or action
            if (notification.actionUrl) {
              window.location.href = notification.actionUrl;
            }
          }}
        />
      </div>
    </header>
  );
}
```

### TypeScript Interfaces

```tsx
export type NotificationType = "info" | "success" | "warning" | "error" | "product" | "message";
export type NotificationPriority = "low" | "medium" | "high" | "urgent";

export interface Notification {
  id: string;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
  metadata?: Record<string, any>;
}

export interface NotificationCenterProps {
  notifications?: Notification[];
  maxDisplay?: number;
  onMarkAsRead?: (notificationId: string) => void;
  onMarkAllAsRead?: () => void;
  onClearAll?: () => void;
  onNotificationClick?: (notification: Notification) => void;
}
```

## Integration Example

Complete example showing both components in a dashboard layout:

```tsx
import { AdvancedMetrics } from '@/components/AdvancedMetrics';
import { NotificationCenter } from '@/components/NotificationCenter';
import { QuickStats } from '@/components/QuickStats';
import { ActiveListings } from '@/components/ActiveListings';

function Dashboard() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header with Notification Center */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur">
        <div className="container flex h-16 items-center justify-between">
          <h1 className="text-xl font-bold">Wall-E Dashboard</h1>
          <div className="flex items-center gap-4">
            <NotificationCenter />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-6 space-y-6">
        {/* Quick Stats */}
        <QuickStats />

        {/* Advanced Metrics */}
        <AdvancedMetrics />

        {/* Active Listings */}
        <ActiveListings />
      </main>
    </div>
  );
}

export default Dashboard;
```

## Features

### AdvancedMetrics Features:
- 4 overview cards with trend indicators (Sales, Messages, Automation, Users)
- Progress bars showing target completion
- Tabbed detailed views for each metric category
- Responsive design (mobile-first)
- Loading states with skeleton loaders
- Spanish language UI
- Professional animations and hover effects

### NotificationCenter Features:
- Bell icon with unread count badge
- Dropdown panel with scrollable notification list
- Notification filtering by type (warnings, products, messages, success)
- Mark individual notifications as read
- Mark all as read functionality
- Clear all notifications
- Priority badges (urgent, high, medium, low)
- Relative timestamp formatting (hace 5m, hace 2h, etc.)
- Click handlers for custom actions
- Spanish language UI
- Responsive design

## Styling

Both components use:
- shadcn-ui components for consistent design
- Tailwind CSS for styling
- lucide-react icons
- Dark mode support
- Professional color scheme with semantic colors
- Smooth transitions and animations
