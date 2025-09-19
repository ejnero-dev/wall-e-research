import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Zap, Users, ShoppingCart, MessageSquare, AlertCircle, Clock, Target } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
    period: string;
  };
  progress?: number;
  icon: React.ElementType;
  color: string;
  description?: string;
  target?: number;
}

const MetricCard = ({ title, value, change, progress, icon: Icon, color, description, target }: MetricCardProps) => {
  const getTrendIcon = () => {
    if (!change) return null;
    return change.type === 'increase' ? TrendingUp : change.type === 'decrease' ? TrendingDown : null;
  };
  
  const TrendIcon = getTrendIcon();
  
  return (
    <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
      <div className={cn("absolute top-0 left-0 h-1 w-full", color)} />
      
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={cn("h-4 w-4 transition-colors", color.replace('bg-', 'text-'))} />
      </CardHeader>
      
      <CardContent className="space-y-3">
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-bold">{value}</div>
          {change && (
            <div className={cn(
              "flex items-center gap-1 text-xs",
              change.type === 'increase' ? 'text-green-600 dark:text-green-400' :
              change.type === 'decrease' ? 'text-red-600 dark:text-red-400' :
              'text-muted-foreground'
            )}>
              {TrendIcon && <TrendIcon className="h-3 w-3" />}
              <span>{Math.abs(change.value)}%</span>
            </div>
          )}
        </div>
        
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
        
        {progress !== undefined && (
          <div className="space-y-1">
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{change?.period || 'Progreso'}</span>
              {target && (
                <span>Meta: {target}</span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

interface AdvancedMetricsProps {
  data?: {
    sales: {
      total: number;
      thisMonth: number;
      target: number;
      change: number;
    };
    messages: {
      total: number;
      rate: number;
      responseTime: number;
      change: number;
    };
    automation: {
      activeScrapers: number;
      successRate: number;
      uptime: number;
      change: number;
    };
    users: {
      activeConversations: number;
      fraudDetected: number;
      conversion: number;
      change: number;
    };
  };
}

export const AdvancedMetrics = ({ data }: AdvancedMetricsProps) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}min`;
    return `${Math.round(seconds / 3600)}h`;
  };

  if (!data) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <div className="text-center space-y-2">
            <AlertCircle className="h-8 w-8 mx-auto text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No hay datos disponibles</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const metrics = [
    {
      title: "Ventas Totales",
      value: formatCurrency(data.sales.total),
      change: {
        value: data.sales.change,
        type: data.sales.change > 0 ? 'increase' as const : 'decrease' as const,
        period: 'Este mes'
      },
      progress: (data.sales.thisMonth / data.sales.target) * 100,
      icon: ShoppingCart,
      color: "bg-emerald-500",
      description: `${formatCurrency(data.sales.thisMonth)} de ${formatCurrency(data.sales.target)} objetivo`,
      target: data.sales.target
    },
    {
      title: "Mensajes/Hora",
      value: Math.round(data.messages.rate),
      change: {
        value: data.messages.change,
        type: data.messages.change > 0 ? 'increase' as const : 'decrease' as const,
        period: 'Última hora'
      },
      progress: Math.min((data.messages.rate / 50) * 100, 100),
      icon: MessageSquare,
      color: "bg-blue-500",
      description: `Tiempo respuesta: ${formatTime(data.messages.responseTime)}`
    },
    {
      title: "Automatización",
      value: `${Math.round(data.automation.successRate)}%`,
      change: {
        value: data.automation.change,
        type: data.automation.change > 0 ? 'increase' as const : 'decrease' as const,
        period: 'Última semana'
      },
      progress: data.automation.successRate,
      icon: Zap,
      color: "bg-purple-500",
      description: `${data.automation.activeScrapers} scrapers activos, ${data.automation.uptime}% uptime`
    },
    {
      title: "Conversaciones",
      value: data.users.activeConversations,
      change: {
        value: data.users.change,
        type: data.users.change > 0 ? 'increase' as const : 'decrease' as const,
        period: 'Hoy'
      },
      progress: (data.users.conversion / 100) * 100,
      icon: Users,
      color: "bg-orange-500",
      description: `${data.users.fraudDetected} fraudes detectados, ${data.users.conversion}% conversión`
    }
  ];

  return (
    <div className="space-y-6">
      {/* Métricas principales */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      {/* Detalles por categorías */}
      <Tabs defaultValue="sales" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="sales">Ventas</TabsTrigger>
          <TabsTrigger value="messages">Mensajes</TabsTrigger>
          <TabsTrigger value="automation">Automatización</TabsTrigger>
          <TabsTrigger value="users">Usuarios</TabsTrigger>
        </TabsList>

        <TabsContent value="sales" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5" />
                Rendimiento de Ventas
              </CardTitle>
              <CardDescription>
                Análisis detallado de tus ventas y objetivos
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Ventas este mes</span>
                    <Badge variant="secondary">{formatCurrency(data.sales.thisMonth)}</Badge>
                  </div>
                  <Progress value={(data.sales.thisMonth / data.sales.target) * 100} className="h-2" />
                  <p className="text-xs text-muted-foreground">
                    {Math.round((data.sales.thisMonth / data.sales.target) * 100)}% del objetivo alcanzado
                  </p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Crecimiento</span>
                    <Badge variant={data.sales.change > 0 ? "default" : "destructive"}>
                      {data.sales.change > 0 ? '+' : ''}{data.sales.change}%
                    </Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Comparado con el mes anterior
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Objetivo anual</span>
                    <Badge variant="outline">{formatCurrency(data.sales.target * 12)}</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Proyección basada en objetivos mensuales
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="messages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Gestión de Mensajes
              </CardTitle>
              <CardDescription>
                Estadísticas de comunicación y respuesta automática
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Mensajes procesados</span>
                    <Badge>{data.messages.total}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Tasa por hora</span>
                    <Badge variant="secondary">{Math.round(data.messages.rate)}/h</Badge>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Tiempo respuesta</span>
                    <Badge variant="outline">{formatTime(data.messages.responseTime)}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      Promedio de respuesta automática
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="automation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Sistema de Automatización
              </CardTitle>
              <CardDescription>
                Estado y rendimiento de los sistemas automatizados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center space-y-2">
                  <div className="text-2xl font-bold text-primary">{data.automation.activeScrapers}</div>
                  <p className="text-sm text-muted-foreground">Scrapers Activos</p>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-2xl font-bold text-green-600">{Math.round(data.automation.successRate)}%</div>
                  <p className="text-sm text-muted-foreground">Tasa de Éxito</p>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-2xl font-bold text-blue-600">{data.automation.uptime}%</div>
                  <p className="text-sm text-muted-foreground">Tiempo Activo</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Gestión de Usuarios
              </CardTitle>
              <CardDescription>
                Análisis de conversaciones y detección de fraude
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <Card className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">Conversaciones Activas</span>
                    </div>
                    <div className="text-2xl font-bold">{data.users.activeConversations}</div>
                    <p className="text-xs text-muted-foreground">En tiempo real</p>
                  </Card>
                  
                  <Card className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertCircle className="h-4 w-4 text-red-500" />
                      <span className="text-sm font-medium">Fraudes Detectados</span>
                    </div>
                    <div className="text-2xl font-bold">{data.users.fraudDetected}</div>
                    <p className="text-xs text-muted-foreground">Sistema de protección</p>
                  </Card>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Tasa de Conversión</span>
                    <Badge variant="secondary">{data.users.conversion}%</Badge>
                  </div>
                  <Progress value={data.users.conversion} className="h-2" />
                  <p className="text-xs text-muted-foreground">
                    Conversaciones que resultan en ventas
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};