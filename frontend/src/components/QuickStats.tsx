import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { TrendingUp, MessageSquare, Eye, DollarSign, AlertTriangle, TrendingDown, Minus } from "lucide-react";
import { useMetrics, useProductStats } from "@/hooks/useAPI";
import { cn } from "@/lib/utils";

export const QuickStats = () => {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useMetrics();
  const { data: productStats, isLoading: statsLoading } = useProductStats();

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}k`;
    }
    return num.toString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  if (metricsLoading || statsLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-4" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-2" />
              <Skeleton className="h-4 w-20" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (metricsError) {
    return (
      <Card className="col-span-full">
        <CardContent className="flex items-center justify-center p-6">
          <div className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            <span>Error al cargar métricas del sistema</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Función para determinar tendencia
  const getTrendData = (current: number, previous?: number) => {
    if (!previous || previous === 0) return { trend: 'neutral', percentage: 0 };
    const change = ((current - previous) / previous) * 100;
    return {
      trend: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral',
      percentage: Math.abs(change)
    };
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return TrendingUp;
      case 'down': return TrendingDown;
      default: return Minus;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-green-600 dark:text-green-400';
      case 'down': return 'text-red-600 dark:text-red-400';
      default: return 'text-muted-foreground';
    }
  };

  const stats = [
    {
      title: "Anuncios Activos",
      value: productStats?.active?.toString() || "0",
      change: productStats?.total ? `${productStats.total} total` : "Sin datos",
      icon: Eye,
      progress: productStats?.active ? (productStats.active / (productStats.total || 1)) * 100 : 0,
      trend: getTrendData(productStats?.active || 0, productStats?.previous_active),
      color: "bg-blue-500",
    },
    {
      title: "Mensajes/Hora",
      value: Math.round(metrics?.msg_rate || 0).toString(),
      change: `${metrics?.total_messages_today || 0} hoy`,
      icon: MessageSquare,
      progress: Math.min((metrics?.msg_rate || 0) * 10, 100),
      trend: getTrendData(metrics?.msg_rate || 0, metrics?.previous_msg_rate),
      color: "bg-green-500",
    },
    {
      title: "Ingresos Mes",
      value: formatCurrency(productStats?.revenue_this_month || 0),
      change: `${productStats?.sold || 0} vendidos`,
      icon: DollarSign,
      progress: productStats?.revenue_this_month ? (productStats.revenue_this_month / (productStats.revenue_goal || 5000)) * 100 : 0,
      trend: getTrendData(productStats?.revenue_this_month || 0, productStats?.previous_revenue),
      color: "bg-emerald-500",
    },
    {
      title: "Tasa Éxito",
      value: `${Math.round(metrics?.success_rate || 0)}%`,
      change: `${metrics?.active_scrapers || 0} scrapers`,
      icon: TrendingUp,
      progress: metrics?.success_rate || 0,
      trend: getTrendData(metrics?.success_rate || 0, metrics?.previous_success_rate),
      color: "bg-purple-500",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => {
        const TrendIcon = getTrendIcon(stat.trend.trend);
        return (
          <Card key={stat.title} className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
            {/* Accent bar */}
            <div className={cn("absolute top-0 left-0 h-1 w-full", stat.color)} />
            
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className="flex items-center gap-2">
                {stat.trend.percentage > 0 && (
                  <div className={cn("flex items-center gap-1 text-xs", getTrendColor(stat.trend.trend))}>
                    <TrendIcon className="h-3 w-3" />
                    <span>{stat.trend.percentage.toFixed(1)}%</span>
                  </div>
                )}
                <stat.icon className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
              </div>
            </CardHeader>
            
            <CardContent className="space-y-3">
              <div className="text-2xl font-bold text-foreground group-hover:scale-105 transition-transform duration-200">
                {stat.value}
              </div>
              
              {/* Progress indicator */}
              <div className="space-y-1">
                <Progress value={stat.progress} className="h-2" />
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">{stat.change}</span>
                  <span className="text-muted-foreground">tiempo real</span>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};