import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ShoppingCart,
  MessageSquare,
  Zap,
  Users,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Clock,
  Target,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Types for component props
interface MetricData {
  current: number;
  target: number;
  change: number;
  trend: "up" | "down" | "neutral";
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

export interface AdvancedMetricsProps {
  data?: {
    sales?: SalesMetrics;
    messages?: MessagesMetrics;
    automation?: AutomationMetrics;
    users?: UsersMetrics;
  };
  isLoading?: boolean;
}

export const AdvancedMetrics = ({ data, isLoading = false }: AdvancedMetricsProps) => {
  const [activeTab, setActiveTab] = useState("sales");

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}k`;
    }
    return num.toString();
  };

  const getTrendIcon = (trend: "up" | "down" | "neutral") => {
    return trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Activity;
  };

  const getTrendColor = (trend: "up" | "down" | "neutral") => {
    return trend === "up"
      ? "text-green-600 dark:text-green-400"
      : trend === "down"
      ? "text-red-600 dark:text-red-400"
      : "text-muted-foreground";
  };

  // Default data if not provided
  const defaultData = {
    sales: {
      total: 0,
      today: 0,
      thisWeek: 0,
      thisMonth: 0,
      target: 10000,
      averageValue: 0,
      conversionRate: 0,
    },
    messages: {
      total: 0,
      messagesPerHour: 0,
      responseTime: 0,
      automatedResponses: 0,
      pendingMessages: 0,
    },
    automation: {
      activeScrapers: 0,
      successRate: 0,
      uptime: 0,
      tasksCompleted: 0,
      errorCount: 0,
    },
    users: {
      totalUsers: 0,
      activeUsers: 0,
      newUsers: 0,
      engagementRate: 0,
    },
  };

  const metricsData = { ...defaultData, ...data };

  // Calculate metrics with trends
  const metrics: Record<string, MetricData> = {
    sales: {
      current: metricsData.sales?.thisMonth || 0,
      target: metricsData.sales?.target || 10000,
      change: 12.5,
      trend: "up",
    },
    messages: {
      current: metricsData.messages?.messagesPerHour || 0,
      target: 50,
      change: -5.2,
      trend: "down",
    },
    automation: {
      current: metricsData.automation?.successRate || 0,
      target: 100,
      change: 8.3,
      trend: "up",
    },
    users: {
      current: metricsData.users?.activeUsers || 0,
      target: 1000,
      change: 15.8,
      trend: "up",
    },
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-20 w-full" />
              </div>
            ))}
          </div>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Metricas Avanzadas
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overview Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* Sales Card */}
          <Card className="relative overflow-hidden group hover:shadow-md transition-all">
            <div className="absolute top-0 left-0 h-1 w-full bg-emerald-500" />
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-2">
                <ShoppingCart className="h-5 w-5 text-emerald-500" />
                <div className={cn("flex items-center gap-1 text-xs", getTrendColor(metrics.sales.trend))}>
                  {(() => {
                    const Icon = getTrendIcon(metrics.sales.trend);
                    return <Icon className="h-3 w-3" />;
                  })()}
                  <span>{metrics.sales.change.toFixed(1)}%</span>
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold">{formatCurrency(metrics.sales.current)}</p>
                <p className="text-xs text-muted-foreground">Ventas este mes</p>
              </div>
              <Progress value={(metrics.sales.current / metrics.sales.target) * 100} className="h-2 mt-3" />
              <p className="text-xs text-muted-foreground mt-1">
                Objetivo: {formatCurrency(metrics.sales.target)}
              </p>
            </CardContent>
          </Card>

          {/* Messages Card */}
          <Card className="relative overflow-hidden group hover:shadow-md transition-all">
            <div className="absolute top-0 left-0 h-1 w-full bg-blue-500" />
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-2">
                <MessageSquare className="h-5 w-5 text-blue-500" />
                <div className={cn("flex items-center gap-1 text-xs", getTrendColor(metrics.messages.trend))}>
                  {(() => {
                    const Icon = getTrendIcon(metrics.messages.trend);
                    return <Icon className="h-3 w-3" />;
                  })()}
                  <span>{Math.abs(metrics.messages.change).toFixed(1)}%</span>
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold">{Math.round(metrics.messages.current)}</p>
                <p className="text-xs text-muted-foreground">Mensajes/hora</p>
              </div>
              <Progress value={(metrics.messages.current / metrics.messages.target) * 100} className="h-2 mt-3" />
              <p className="text-xs text-muted-foreground mt-1">
                Promedio esperado: {metrics.messages.target}/h
              </p>
            </CardContent>
          </Card>

          {/* Automation Card */}
          <Card className="relative overflow-hidden group hover:shadow-md transition-all">
            <div className="absolute top-0 left-0 h-1 w-full bg-purple-500" />
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-2">
                <Zap className="h-5 w-5 text-purple-500" />
                <div className={cn("flex items-center gap-1 text-xs", getTrendColor(metrics.automation.trend))}>
                  {(() => {
                    const Icon = getTrendIcon(metrics.automation.trend);
                    return <Icon className="h-3 w-3" />;
                  })()}
                  <span>{metrics.automation.change.toFixed(1)}%</span>
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold">{Math.round(metrics.automation.current)}%</p>
                <p className="text-xs text-muted-foreground">Tasa de exito</p>
              </div>
              <Progress value={metrics.automation.current} className="h-2 mt-3" />
              <p className="text-xs text-muted-foreground mt-1">
                {metricsData.automation?.activeScrapers || 0} scrapers activos
              </p>
            </CardContent>
          </Card>

          {/* Users Card */}
          <Card className="relative overflow-hidden group hover:shadow-md transition-all">
            <div className="absolute top-0 left-0 h-1 w-full bg-amber-500" />
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-2">
                <Users className="h-5 w-5 text-amber-500" />
                <div className={cn("flex items-center gap-1 text-xs", getTrendColor(metrics.users.trend))}>
                  {(() => {
                    const Icon = getTrendIcon(metrics.users.trend);
                    return <Icon className="h-3 w-3" />;
                  })()}
                  <span>{metrics.users.change.toFixed(1)}%</span>
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold">{formatNumber(metrics.users.current)}</p>
                <p className="text-xs text-muted-foreground">Usuarios activos</p>
              </div>
              <Progress value={(metrics.users.current / metrics.users.target) * 100} className="h-2 mt-3" />
              <p className="text-xs text-muted-foreground mt-1">
                +{metricsData.users?.newUsers || 0} nuevos esta semana
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="sales" className="flex items-center gap-2">
              <ShoppingCart className="h-4 w-4" />
              <span className="hidden sm:inline">Ventas</span>
            </TabsTrigger>
            <TabsTrigger value="messages" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">Mensajes</span>
            </TabsTrigger>
            <TabsTrigger value="automation" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <span className="hidden sm:inline">Automatizacion</span>
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Usuarios</span>
            </TabsTrigger>
          </TabsList>

          {/* Sales Tab */}
          <TabsContent value="sales" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Ventas Hoy</span>
                  </div>
                  <p className="text-2xl font-bold">{formatCurrency(metricsData.sales?.today || 0)}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {metricsData.sales?.today || 0} transacciones
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Esta Semana</span>
                  </div>
                  <p className="text-2xl font-bold">{formatCurrency(metricsData.sales?.thisWeek || 0)}</p>
                  <Badge variant="secondary" className="mt-2">
                    +{((metricsData.sales?.thisWeek || 0) / 7).toFixed(0)} promedio/dia
                  </Badge>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Conversion</span>
                  </div>
                  <p className="text-2xl font-bold">{(metricsData.sales?.conversionRate || 0).toFixed(1)}%</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Valor promedio: {formatCurrency(metricsData.sales?.averageValue || 0)}
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Messages Tab */}
          <TabsContent value="messages" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Total Mensajes</span>
                  </div>
                  <p className="text-2xl font-bold">{formatNumber(metricsData.messages?.total || 0)}</p>
                  <p className="text-xs text-muted-foreground mt-1">Desde el inicio</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Tiempo Respuesta</span>
                  </div>
                  <p className="text-2xl font-bold">{(metricsData.messages?.responseTime || 0).toFixed(1)}m</p>
                  <Badge variant="secondary" className="mt-2">
                    Promedio
                  </Badge>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Automatizadas</span>
                  </div>
                  <p className="text-2xl font-bold">{formatNumber(metricsData.messages?.automatedResponses || 0)}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {metricsData.messages?.pendingMessages || 0} pendientes
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Automation Tab */}
          <TabsContent value="automation" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Uptime</span>
                  </div>
                  <p className="text-2xl font-bold">{(metricsData.automation?.uptime || 0).toFixed(1)}%</p>
                  <Badge variant="secondary" className="mt-2">
                    Operacional
                  </Badge>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Tareas Completadas</span>
                  </div>
                  <p className="text-2xl font-bold">{formatNumber(metricsData.automation?.tasksCompleted || 0)}</p>
                  <p className="text-xs text-muted-foreground mt-1">Total procesadas</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Errores</span>
                  </div>
                  <p className="text-2xl font-bold">{metricsData.automation?.errorCount || 0}</p>
                  {(metricsData.automation?.errorCount || 0) > 0 ? (
                    <Badge variant="destructive" className="mt-2">
                      Requiere atencion
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="mt-2">
                      Todo OK
                    </Badge>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Total Usuarios</span>
                  </div>
                  <p className="text-2xl font-bold">{formatNumber(metricsData.users?.totalUsers || 0)}</p>
                  <p className="text-xs text-muted-foreground mt-1">Registrados</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Nuevos Usuarios</span>
                  </div>
                  <p className="text-2xl font-bold">{metricsData.users?.newUsers || 0}</p>
                  <Badge variant="secondary" className="mt-2">
                    Esta semana
                  </Badge>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Engagement</span>
                  </div>
                  <p className="text-2xl font-bold">{(metricsData.users?.engagementRate || 0).toFixed(1)}%</p>
                  <p className="text-xs text-muted-foreground mt-1">Tasa de participacion</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
