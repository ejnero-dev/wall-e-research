import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Bell, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  X, 
  Settings,
  Filter,
  MoreHorizontal,
  MessageSquare,
  TrendingUp,
  Package,
  DollarSign
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  category: 'sale' | 'message' | 'system' | 'detection' | 'fraud';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: {
    label: string;
    action: () => void;
  }[];
}

const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'success',
    category: 'sale',
    title: 'Venta realizada',
    message: 'iPhone 12 Pro vendido por 650€. El comprador ha confirmado la transacción.',
    timestamp: '2025-01-09T10:30:00Z',
    read: false,
    actions: [
      { label: 'Ver detalles', action: () => console.log('Ver detalles de venta') },
      { label: 'Contactar', action: () => console.log('Contactar comprador') }
    ]
  },
  {
    id: '2',
    type: 'info',
    category: 'message',
    title: 'Nuevo mensaje',
    message: 'Has recibido 3 mensajes nuevos sobre "MacBook Air M1". Respuesta automática enviada.',
    timestamp: '2025-01-09T10:15:00Z',
    read: false
  },
  {
    id: '3',
    type: 'warning',
    category: 'fraud',
    title: 'Posible fraude detectado',
    message: 'Usuario sospechoso intentó negociar fuera de la plataforma. Conversación bloqueada automáticamente.',
    timestamp: '2025-01-09T09:45:00Z',
    read: true
  },
  {
    id: '4',
    type: 'success',
    category: 'detection',
    title: 'Productos detectados',
    message: '5 productos similares detectados en tu zona con precios competitivos.',
    timestamp: '2025-01-09T09:30:00Z',
    read: true
  },
  {
    id: '5',
    type: 'error',
    category: 'system',
    title: 'Error en scraper',
    message: 'El scraper de Amazon ha fallado. Último intento hace 15 minutos.',
    timestamp: '2025-01-09T09:00:00Z',
    read: false,
    actions: [
      { label: 'Reintentar', action: () => console.log('Reintentar scraper') },
      { label: 'Ver logs', action: () => console.log('Ver logs del scraper') }
    ]
  }
];

const getTypeIcon = (type: Notification['type']) => {
  switch (type) {
    case 'success':
      return CheckCircle;
    case 'error':
      return AlertTriangle;
    case 'warning':
      return AlertTriangle;
    case 'info':
      return Info;
    default:
      return Info;
  }
};

const getCategoryIcon = (category: Notification['category']) => {
  switch (category) {
    case 'sale':
      return DollarSign;
    case 'message':
      return MessageSquare;
    case 'system':
      return Settings;
    case 'detection':
      return Package;
    case 'fraud':
      return AlertTriangle;
    default:
      return Bell;
  }
};

const getTypeColor = (type: Notification['type']) => {
  switch (type) {
    case 'success':
      return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950';
    case 'error':
      return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950';
    case 'warning':
      return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-950';
    case 'info':
      return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950';
    default:
      return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-950';
  }
};

const formatTimeAgo = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'hace menos de 1 minuto';
  if (diffMins < 60) return `hace ${diffMins} minutos`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `hace ${diffHours} horas`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `hace ${diffDays} días`;
};

export const NotificationCenter = () => {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const [categoryFilter, setCategoryFilter] = useState<Notification['category'] | 'all'>('all');

  const filteredNotifications = notifications.filter(notification => {
    const matchesReadFilter = filter === 'all' || 
      (filter === 'read' && notification.read) || 
      (filter === 'unread' && !notification.read);
    
    const matchesCategoryFilter = categoryFilter === 'all' || notification.category === categoryFilter;
    
    return matchesReadFilter && matchesCategoryFilter;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => 
      n.id === id ? { ...n, read: true } : n
    ));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <CardTitle className="text-lg">Notificaciones</CardTitle>
            {unreadCount > 0 && (
              <Badge variant="destructive" className="h-5 min-w-5 text-xs px-1.5">
                {unreadCount}
              </Badge>
            )}
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={markAllAsRead}>
                Marcar todas como leídas
              </DropdownMenuItem>
              <DropdownMenuItem>
                Configurar notificaciones
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        {/* Filtros */}
        <div className="flex items-center gap-2 mt-3">
          <div className="flex bg-muted rounded-md p-1">
            {(['all', 'unread', 'read'] as const).map((filterOption) => (
              <button
                key={filterOption}
                onClick={() => setFilter(filterOption)}
                className={cn(
                  "px-3 py-1 text-xs rounded-sm transition-colors",
                  filter === filterOption 
                    ? "bg-background text-foreground shadow-sm" 
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {filterOption === 'all' ? 'Todas' : 
                 filterOption === 'unread' ? 'No leídas' : 'Leídas'}
              </button>
            ))}
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-8 px-2">
                <Filter className="h-3 w-3 mr-1" />
                {categoryFilter === 'all' ? 'Todo' : categoryFilter}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setCategoryFilter('all')}>
                Todas las categorías
              </DropdownMenuItem>
              <Separator />
              {(['sale', 'message', 'system', 'detection', 'fraud'] as const).map((cat) => {
                const Icon = getCategoryIcon(cat);
                return (
                  <DropdownMenuItem 
                    key={cat} 
                    onClick={() => setCategoryFilter(cat)}
                    className="flex items-center gap-2"
                  >
                    <Icon className="h-4 w-4" />
                    {cat === 'sale' ? 'Ventas' :
                     cat === 'message' ? 'Mensajes' :
                     cat === 'system' ? 'Sistema' :
                     cat === 'detection' ? 'Detección' : 'Fraude'}
                  </DropdownMenuItem>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No hay notificaciones</p>
              <p className="text-sm">
                {filter === 'unread' ? 'Todas las notificaciones han sido leídas' :
                 filter === 'read' ? 'No hay notificaciones leídas' :
                 'Tu bandeja de notificaciones está vacía'}
              </p>
            </div>
          ) : (
            <div className="space-y-1 p-1">
              {filteredNotifications.map((notification, index) => {
                const TypeIcon = getTypeIcon(notification.type);
                const CategoryIcon = getCategoryIcon(notification.category);
                const typeColor = getTypeColor(notification.type);
                
                return (
                  <div
                    key={notification.id}
                    className={cn(
                      "group relative p-3 rounded-lg border transition-all duration-200 hover:shadow-sm cursor-pointer",
                      !notification.read 
                        ? "bg-accent/30 border-accent hover:bg-accent/40" 
                        : "bg-background hover:bg-accent/20",
                      "animate-in slide-in-from-right-2"
                    )}
                    style={{ animationDelay: `${index * 50}ms` }}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                  >
                    {/* Indicador de no leído */}
                    {!notification.read && (
                      <div className="absolute top-3 left-1 w-2 h-2 bg-primary rounded-full" />
                    )}
                    
                    <div className="flex items-start gap-3 pl-2">
                      {/* Ícono de categoría */}
                      <div className="flex-shrink-0 mt-0.5">
                        <div className={cn("p-2 rounded-full", typeColor)}>
                          <CategoryIcon className="h-4 w-4" />
                        </div>
                      </div>
                      
                      {/* Contenido */}
                      <div className="flex-1 min-w-0 space-y-1">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className={cn(
                            "text-sm font-medium truncate",
                            !notification.read && "font-semibold"
                          )}>
                            {notification.title}
                          </h4>
                          <div className="flex items-center gap-1 flex-shrink-0">
                            <TypeIcon className={cn(
                              "h-3 w-3",
                              notification.type === 'success' && "text-green-600 dark:text-green-400",
                              notification.type === 'error' && "text-red-600 dark:text-red-400",
                              notification.type === 'warning' && "text-yellow-600 dark:text-yellow-400",
                              notification.type === 'info' && "text-blue-600 dark:text-blue-400"
                            )} />
                            <Button
                              variant="ghost"
                              size="sm"
                              className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0"
                              onClick={(e) => {
                                e.stopPropagation();
                                removeNotification(notification.id);
                              }}
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {notification.message}
                        </p>
                        
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-muted-foreground">
                            {formatTimeAgo(notification.timestamp)}
                          </span>
                          
                          {/* Acciones */}
                          {notification.actions && (
                            <div className="flex gap-1">
                              {notification.actions.slice(0, 2).map((action, actionIndex) => (
                                <Button
                                  key={actionIndex}
                                  variant="outline"
                                  size="sm"
                                  className="h-6 px-2 text-xs"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    action.action();
                                  }}
                                >
                                  {action.label}
                                </Button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

// Botón de notificaciones para el header
export const NotificationButton = ({ onClick }: { onClick: () => void }) => {
  const unreadCount = mockNotifications.filter(n => !n.read).length;
  
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onClick}
      className="relative p-2"
      aria-label={`Notificaciones${unreadCount > 0 ? ` (${unreadCount} no leídas)` : ''}`}
    >
      <Bell className="h-5 w-5" />
      {unreadCount > 0 && (
        <>
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full animate-pulse" />
          <Badge 
            variant="destructive" 
            className="absolute -top-2 -right-2 h-5 min-w-5 text-xs px-1.5 animate-in zoom-in-50"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </Badge>
        </>
      )}
    </Button>
  );
};