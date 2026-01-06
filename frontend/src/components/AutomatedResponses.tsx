import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, MessageSquare, Settings, AlertTriangle, Activity } from "lucide-react";
import { useConfig, useUpdateConfig } from "@/hooks/useAPI";

export const AutomatedResponses = () => {
  const { data: config, isLoading, error } = useConfig();
  const updateConfigMutation = useUpdateConfig();

  const handleToggleAutoResponse = (enabled: boolean) => {
    updateConfigMutation.mutate({
      key: 'auto_response',
      value: enabled,
      applyImmediately: true,
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-8 w-20" />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3 p-3 border rounded-lg">
              <Skeleton className="h-5 w-10 mt-1" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-5 w-12" />
                </div>
                <Skeleton className="h-4 w-full" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Respuestas Automáticas</CardTitle>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                console.log('Agregando nueva respuesta automática');
                // TODO: Abrir modal para crear nueva respuesta
              }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Nueva
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              <span>Error al cargar configuración</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Template responses (in production these would come from backend)
  const responses = [
    {
      id: "greeting",
      title: "Saludo inicial",
      message: "¡Hola! Gracias por tu interés. ¿Te gustaría saber algo específico del producto?",
      enabled: config?.auto_response || false,
      used: Math.floor(Math.random() * 30) + 10, // Mock usage
    },
    {
      id: "price_inquiry",
      title: "Consulta de precio",
      message: "El precio mostrado es fijo. No acepto intercambios por el momento.",
      enabled: config?.auto_response || false,
      used: Math.floor(Math.random() * 20) + 5,
    },
    {
      id: "availability",
      title: "Disponibilidad",
      message: "Sí, el artículo sigue disponible. ¿Cuándo te vendría bien verlo?",
      enabled: config?.auto_response || false,
      used: Math.floor(Math.random() * 15) + 3,
    },
    {
      id: "delivery",
      title: "Entrega/Recogida",
      message: "Prefiero entrega en mano en zona centro. También acepto envío con gastos aparte.",
      enabled: config?.auto_response || false,
      used: Math.floor(Math.random() * 25) + 8,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">Respuestas Automáticas</CardTitle>
            <Badge variant={config?.auto_response ? "default" : "secondary"} className="text-xs">
              <Activity className="w-3 h-3 mr-1" />
              {config?.auto_response ? "Activo" : "Inactivo"}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              checked={config?.auto_response || false}
              onCheckedChange={handleToggleAutoResponse}
              disabled={updateConfigMutation.isPending}
            />
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                console.log('Abriendo configuración de respuestas automáticas');
                // TODO: Abrir panel de configuración
              }}
            >
              <Settings className="w-4 h-4 mr-2" />
              Configurar
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground mb-4">
          {config?.auto_response 
            ? `Configuración actual: ${config.msg_per_hour} msgs/hora, ${config.timeout}s timeout`
            : "Las respuestas automáticas están desactivadas"
          }
        </div>
        {responses.map((response) => (
          <div
            key={response.id}
            className={`flex items-start gap-3 p-3 border rounded-lg transition-colors ${
              response.enabled 
                ? "hover:bg-accent/50" 
                : "opacity-50 bg-muted/20"
            }`}
          >
            <div className="mt-1">
              {response.enabled ? (
                <div className="w-2 h-2 bg-green-500 rounded-full" />
              ) : (
                <div className="w-2 h-2 bg-gray-400 rounded-full" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-medium text-sm">{response.title}</h4>
                <Badge variant="secondary" className="text-xs">
                  <MessageSquare className="w-3 h-3 mr-1" />
                  {response.used}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {response.message}
              </p>
            </div>
          </div>
        ))}
        
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              Total respuestas enviadas hoy: {responses.reduce((sum, r) => sum + r.used, 0)}
            </span>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => {
                console.log('Agregando nueva plantilla de respuesta');
                // TODO: Abrir formulario para nueva plantilla
              }}
            >
              <Plus className="w-4 h-4 mr-1" />
              Agregar plantilla
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};