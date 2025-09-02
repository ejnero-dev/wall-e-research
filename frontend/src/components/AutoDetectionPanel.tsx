import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"; 
import { cn } from "@/lib/utils";
import { 
  Bot, 
  Search, 
  Play, 
  Pause, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  MessageSquare
} from "lucide-react";
import { 
  useAutoDetectionStatus, 
  useStartAutoDetection, 
  useStopAutoDetection,
  useManualScan,
  useDetectedProducts,
  useAutoDetectionStatistics
} from "@/hooks/useAPI";

export const AutoDetectionPanel = () => {
  const { data: status, isLoading: statusLoading, error: statusError } = useAutoDetectionStatus();
  const { data: detectedProducts, isLoading: productsLoading } = useDetectedProducts();
  const { data: statistics, isLoading: statsLoading } = useAutoDetectionStatistics();
  
  const startMutation = useStartAutoDetection();
  const stopMutation = useStopAutoDetection();
  const scanMutation = useManualScan();

  const handleToggleDetection = () => {
    if (status?.is_running) {
      stopMutation.mutate();
    } else {
      startMutation.mutate();
    }
  };

  const handleManualScan = () => {
    scanMutation.mutate();
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

  if (statusLoading || statsLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-8 w-24" />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-20 w-full" />
          <div className="grid grid-cols-2 gap-4">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (statusError) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="w-5 h-5" />
              Auto-detección de Productos
            </CardTitle>
            <Badge variant="destructive">Error</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              <span>Error al cargar sistema de auto-detección</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusBadge = () => {
    if (status?.is_running) {
      return (
        <Badge className="bg-green-500">
          <CheckCircle className="w-3 h-3 mr-1" />
          Activo
        </Badge>
      );
    }
    return (
      <Badge variant="secondary">
        <Clock className="w-3 h-3 mr-1" />
        Inactivo
      </Badge>
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="w-5 h-5" />
              Auto-detección de Productos
            </CardTitle>
            {getStatusBadge()}
          </div>
          
          <div className="flex items-center gap-2">
            <Switch
              checked={status?.is_running || false}
              onCheckedChange={handleToggleDetection}
              disabled={startMutation.isPending || stopMutation.isPending}
            />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                console.log('Abriendo configuración de auto-detección');
                // TODO: Abrir panel de configuración
              }}
            >
              <Settings className="w-4 h-4 mr-2" />
              Config
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Status Information with improved visual hierarchy */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4 text-center hover:shadow-sm transition-shadow">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Search className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-muted-foreground">Detectados</span>
            </div>
            <div className="text-2xl font-bold text-primary">
              {statistics?.statistics?.products_detected || status?.products_detected || 0}
            </div>
            <Progress 
              value={Math.min(((statistics?.statistics?.products_detected || 0) / 100) * 100, 100)} 
              className="h-1 mt-2" 
            />
          </Card>
          
          <Card className="p-4 text-center hover:shadow-sm transition-shadow">
            <div className="flex items-center justify-center gap-2 mb-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-muted-foreground">Gestionados</span>
            </div>
            <div className="text-2xl font-bold text-primary">
              {status?.total_products_managed || 0}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {status?.total_products_managed ? 
                `${Math.round((status.total_products_managed / Math.max(status.products_detected || 1, 1)) * 100)}% procesados` : 
                'Esperando productos'
              }
            </div>
          </Card>
          
          <Card className="p-4 text-center hover:shadow-sm transition-shadow">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-medium text-muted-foreground">Último Escaneo</span>
            </div>
            <div className="text-sm font-bold text-primary">
              {status?.last_scan ? formatTimeAgo(status.last_scan) : 'Nunca'}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {status?.is_running ? 'Sistema activo' : 'Sistema pausado'}
            </div>
          </Card>
        </div>

        {/* Enhanced Manual Scan with better UX */}
        <Card className="p-4 border-dashed hover:border-solid transition-all duration-200">
          <div className="flex items-center justify-between">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-primary/10 rounded-full">
                <Search className="w-4 h-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium flex items-center gap-2">
                  Escaneo Manual
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <AlertTriangle className="w-3 h-3 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Ejecuta un escaneo inmediato independiente del programado</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </h4>
                <p className="text-sm text-muted-foreground">
                  Ejecutar un escaneo inmediato de productos disponibles
                </p>
                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <span>• Tiempo estimado: 2-5 min</span>
                  <span>• Cobertura: Todas las categorías</span>
                </div>
              </div>
            </div>
            <Button
              onClick={handleManualScan}
              disabled={scanMutation.isPending || status?.is_running}
              size="sm"
              className={cn(
                "transition-all duration-200",
                scanMutation.isPending && "animate-pulse"
              )}
            >
              {scanMutation.isPending ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                  Escaneando...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Escanear Ahora
                </>
              )}
            </Button>
          </div>
          {scanMutation.isPending && (
            <div className="mt-3 pt-3 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progreso del escaneo</span>
                <span className="text-primary">Analizando productos...</span>
              </div>
              <Progress value={65} className="h-2 mt-2" />
            </div>
          )}
        </Card>

        {/* Detected Products Preview */}
        {!productsLoading && detectedProducts && detectedProducts.length > 0 && (
          <div>
            <h4 className="font-medium mb-3">Productos Detectados Recientemente</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {detectedProducts.slice(0, 5).map((product, index) => (
                <div
                  key={product.id}
                  className="group flex items-center gap-3 p-3 border rounded-lg hover:bg-accent/50 hover:shadow-sm transition-all duration-200"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <Avatar className="h-10 w-10 rounded-md">
                    <AvatarImage src={product.image_url} alt={product.title} />
                    <AvatarFallback className="rounded-md text-xs bg-primary/10">
                      {product.title.split(' ').map(word => word[0]).join('').slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 min-w-0 space-y-1">
                    <h5 className="font-medium text-sm truncate group-hover:text-primary transition-colors" title={product.title}>
                      {product.title}
                    </h5>
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-primary font-semibold">
                        €{product.price}
                      </p>
                      <Badge variant="outline" className="text-xs h-5">
                        {product.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Detectado {formatTimeAgo(product.created_at)}
                    </p>
                  </div>
                  
                  <div className="hidden sm:flex items-center gap-3 text-sm text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger>
                          <div className="flex items-center gap-1 hover:text-foreground transition-colors">
                            <Eye className="w-4 h-4" />
                            <span>{product.views}</span>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Visualizaciones del producto</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                    
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger>
                          <div className={cn(
                            "flex items-center gap-1 hover:text-foreground transition-colors",
                            product.messages_count > 0 && "text-green-600 dark:text-green-400"
                          )}>
                            <MessageSquare className="w-4 h-4" />
                            <span>{product.messages_count}</span>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Mensajes recibidos</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </div>
              ))}
            </div>
            
            {detectedProducts.length > 5 && (
              <div className="text-center pt-3">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {
                    console.log('Mostrando todos los productos detectados:', detectedProducts.length);
                    // TODO: Navegar a vista completa de productos detectados
                  }}
                >
                  Ver todos ({detectedProducts.length})
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!productsLoading && (!detectedProducts || detectedProducts.length === 0) && (
          <div className="text-center py-8 text-muted-foreground">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No hay productos detectados aún</p>
            <p className="text-sm">
              {status?.is_running 
                ? "El sistema está escaneando activamente..."
                : "Activa la auto-detección para comenzar"
              }
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};