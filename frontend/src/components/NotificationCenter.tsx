import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Bell,
  AlertTriangle,
  Info,
  CheckCircle,
  X,
  Settings,
  Filter,
  AlertCircle,
  ShoppingCart,
  MessageSquare,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Notification types
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

export const NotificationCenter = ({
  notifications = [],
  maxDisplay = 50,
  onMarkAsRead,
  onMarkAllAsRead,
  onClearAll,
  onNotificationClick,
}: NotificationCenterProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<NotificationType | "all">("all");
  const [localNotifications, setLocalNotifications] = useState<Notification[]>(notifications);

  // Update local notifications when props change
  useEffect(() => {
    setLocalNotifications(notifications);
  }, [notifications]);

  // Sample notifications if none provided
  useEffect(() => {
    if (notifications.length === 0) {
      setLocalNotifications([
        {
          id: "1",
          type: "warning",
          priority: "high",
          title: "Posible fraude detectado",
          message: "Se ha detectado un intento de fraude en la conversacion con el usuario @comprador123",
          timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
          read: false,
        },
        {
          id: "2",
          type: "success",
          priority: "medium",
          title: "Venta completada",
          message: "Producto 'iPhone 12 Pro' vendido por 450€",
          timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
          read: false,
        },
        {
          id: "3",
          type: "info",
          priority: "low",
          title: "Nuevo mensaje recibido",
          message: "Has recibido un nuevo mensaje sobre 'MacBook Air M1'",
          timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
          read: true,
        },
        {
          id: "4",
          type: "product",
          priority: "medium",
          title: "Producto detectado automaticamente",
          message: "Se ha encontrado un nuevo producto que coincide con tus criterios: 'PlayStation 5'",
          timestamp: new Date(Date.now() - 4 * 60 * 60000).toISOString(),
          read: true,
        },
      ]);
    }
  }, [notifications.length]);

  // Filter notifications
  const filteredNotifications = filter === "all"
    ? localNotifications
    : localNotifications.filter((n) => n.type === filter);

  // Get unread count
  const unreadCount = localNotifications.filter((n) => !n.read).length;

  // Get icon for notification type
  const getNotificationIcon = (type: NotificationType) => {
    switch (type) {
      case "success":
        return CheckCircle;
      case "warning":
        return AlertTriangle;
      case "error":
        return AlertCircle;
      case "product":
        return ShoppingCart;
      case "message":
        return MessageSquare;
      default:
        return Info;
    }
  };

  // Get color for notification type
  const getNotificationColor = (type: NotificationType) => {
    switch (type) {
      case "success":
        return "text-green-500";
      case "warning":
        return "text-amber-500";
      case "error":
        return "text-red-500";
      case "product":
        return "text-blue-500";
      case "message":
        return "text-purple-500";
      default:
        return "text-blue-500";
    }
  };

  // Get background color for notification type
  const getNotificationBgColor = (type: NotificationType, read: boolean) => {
    const opacity = read ? "bg-opacity-5" : "bg-opacity-10";
    switch (type) {
      case "success":
        return `bg-green-500 ${opacity}`;
      case "warning":
        return `bg-amber-500 ${opacity}`;
      case "error":
        return `bg-red-500 ${opacity}`;
      case "product":
        return `bg-blue-500 ${opacity}`;
      case "message":
        return `bg-purple-500 ${opacity}`;
      default:
        return `bg-blue-500 ${opacity}`;
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Ahora mismo";
    if (diffMins < 60) return `Hace ${diffMins}m`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    return date.toLocaleDateString("es-ES", { day: "numeric", month: "short" });
  };

  // Handle mark as read
  const handleMarkAsRead = (notificationId: string) => {
    setLocalNotifications((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
    );
    onMarkAsRead?.(notificationId);
  };

  // Handle mark all as read
  const handleMarkAllAsRead = () => {
    setLocalNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    onMarkAllAsRead?.();
  };

  // Handle clear all
  const handleClearAll = () => {
    setLocalNotifications([]);
    onClearAll?.();
  };

  // Handle notification click
  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      handleMarkAsRead(notification.id);
    }
    onNotificationClick?.(notification);
  };

  // Get priority badge
  const getPriorityBadge = (priority: NotificationPriority) => {
    switch (priority) {
      case "urgent":
        return <Badge variant="destructive" className="text-xs">Urgente</Badge>;
      case "high":
        return <Badge variant="destructive" className="text-xs bg-amber-500">Alta</Badge>;
      case "medium":
        return <Badge variant="secondary" className="text-xs">Media</Badge>;
      default:
        return null;
    }
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
          <span className="sr-only">Notificaciones</span>
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-[400px] p-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <h3 className="font-semibold">Notificaciones</h3>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {unreadCount} nueva{unreadCount !== 1 ? "s" : ""}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-1">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Filter className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setFilter("all")}>
                  <span className={cn(filter === "all" && "font-semibold")}>Todas</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setFilter("warning")}>
                  <AlertTriangle className="h-4 w-4 mr-2 text-amber-500" />
                  Advertencias
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilter("product")}>
                  <ShoppingCart className="h-4 w-4 mr-2 text-blue-500" />
                  Productos
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilter("message")}>
                  <MessageSquare className="h-4 w-4 mr-2 text-purple-500" />
                  Mensajes
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilter("success")}>
                  <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                  Exitos
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Notifications List */}
        <ScrollArea className="h-[400px]">
          {filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center">
              <Bell className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-sm font-medium text-muted-foreground">No hay notificaciones</p>
              <p className="text-xs text-muted-foreground mt-1">
                Te notificaremos cuando haya novedades
              </p>
            </div>
          ) : (
            <div className="divide-y">
              {filteredNotifications.slice(0, maxDisplay).map((notification) => {
                const Icon = getNotificationIcon(notification.type);
                const iconColor = getNotificationColor(notification.type);
                const bgColor = getNotificationBgColor(notification.type, notification.read);

                return (
                  <div
                    key={notification.id}
                    className={cn(
                      "group relative p-4 cursor-pointer transition-colors hover:bg-accent/50",
                      !notification.read && "border-l-4 border-l-primary",
                      bgColor
                    )}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    {/* Unread indicator dot */}
                    {!notification.read && (
                      <div className="absolute top-4 left-2 h-2 w-2 rounded-full bg-primary" />
                    )}

                    <div className="flex items-start gap-3">
                      {/* Icon */}
                      <div className={cn("mt-0.5", iconColor)}>
                        <Icon className="h-5 w-5" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0 space-y-1">
                        <div className="flex items-start justify-between gap-2">
                          <p className={cn("text-sm font-medium", !notification.read && "font-semibold")}>
                            {notification.title}
                          </p>
                          {getPriorityBadge(notification.priority)}
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2">{notification.message}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>{formatTimestamp(notification.timestamp)}</span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkAsRead(notification.id);
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>

        {/* Footer Actions */}
        {filteredNotifications.length > 0 && (
          <>
            <Separator />
            <div className="p-2 flex items-center justify-between gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs"
                onClick={handleMarkAllAsRead}
                disabled={unreadCount === 0}
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Marcar todas como leidas
              </Button>
              <Button variant="ghost" size="sm" className="text-xs" onClick={handleClearAll}>
                <X className="h-4 w-4 mr-1" />
                Limpiar todo
              </Button>
            </div>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
