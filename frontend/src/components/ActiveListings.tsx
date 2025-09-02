import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Eye, MessageCircle, Settings, Plus, AlertTriangle, MoreVertical, Edit, Pause, Play, Trash2, ExternalLink } from "lucide-react";
import { useProducts } from "@/hooks/useAPI";
import { cn } from "@/lib/utils";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";

export const ActiveListings = () => {
  const { data: products, isLoading, error } = useProducts();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-500 text-white">Activo</Badge>;
      case "paused":
        return <Badge variant="secondary">Pausado</Badge>;
      case "sold":
        return <Badge className="bg-blue-500 text-white">Vendido</Badge>;
      case "expired":
        return <Badge variant="destructive">Expirado</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-8 w-20" />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="h-5 w-16" />
                </div>
                <Skeleton className="h-4 w-20" />
              </div>
              <div className="flex items-center gap-4">
                <Skeleton className="h-4 w-12" />
                <Skeleton className="h-4 w-12" />
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
            <CardTitle className="text-lg">Anuncios Activos</CardTitle>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Gestionar
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-6">
            <div className="flex flex-col items-center gap-4">
              <div className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                <span>Error al cargar productos</span>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  console.log('Reintentando cargar productos');
                  window.location.reload();
                }}
              >
                Reintentar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const activeProducts = products?.filter(product => 
    product.status === 'active' || product.status === 'paused'
  ).slice(0, 6) || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Anuncios Activos ({activeProducts.length})</CardTitle>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                console.log('Agregando nuevo producto');
                // TODO: Abrir modal/formulario para agregar producto
              }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Agregar
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                console.log('Gestionando todos los productos');
                // TODO: Navegar a página de gestión de productos
              }}
            >
              <Settings className="w-4 h-4 mr-2" />
              Gestionar
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {activeProducts.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p>No hay productos activos</p>
            <p className="text-sm">Agrega tu primer producto para empezar</p>
          </div>
        ) : (
          activeProducts.map((product) => (
            <div
              key={product.id}
              className="group relative flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 hover:shadow-md hover:border-accent transition-all duration-200 cursor-pointer"
            >
              {/* Product Image Placeholder */}
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <Avatar className="h-12 w-12 rounded-md">
                  <AvatarImage src={product.image_url} alt={product.title} />
                  <AvatarFallback className="rounded-md text-xs bg-primary/10">
                    {product.title.split(' ').map(word => word[0]).join('').slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-sm truncate group-hover:text-primary transition-colors" title={product.title}>
                      {product.title}
                    </h4>
                    {getStatusBadge(product.status)}
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <p className="text-primary font-semibold">{formatCurrency(product.price)}</p>
                    {product.original_price && product.original_price > product.price && (
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger>
                            <span className="text-xs text-muted-foreground line-through">
                              {formatCurrency(product.original_price)}
                            </span>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Precio original antes del descuento</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    )}
                  </div>
                  
                  {product.location && (
                    <p className="text-xs text-muted-foreground">{product.location}</p>
                  )}
                </div>
              </div>
              
              {/* Stats and Actions */}
              <div className="flex items-center gap-4">
                {/* Stats */}
                <div className="hidden sm:flex items-center gap-4 text-sm text-muted-foreground">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <div className="flex items-center gap-1 hover:text-foreground transition-colors">
                          <Eye className="w-4 h-4" />
                          <span>{product.views}</span>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Visualizaciones del anuncio</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <div className={cn(
                          "flex items-center gap-1 hover:text-foreground transition-colors",
                          product.messages_received > 0 && "text-green-600 dark:text-green-400"
                        )}>
                          <MessageCircle className="w-4 h-4" />
                          <span>{product.messages_received}</span>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Mensajes recibidos</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                
                {/* Actions Menu */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0"
                    >
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">Abrir menú</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => {
                      console.log('Abriendo producto en Wallapop:', product.wallapop_url);
                      window.open(product.wallapop_url, '_blank');
                    }}>
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Ver en Wallapop
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => {
                      console.log('Editando producto:', product.id);
                      // TODO: Abrir modal de edición
                    }}>
                      <Edit className="mr-2 h-4 w-4" />
                      Editar producto
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => {
                      console.log(product.status === 'active' ? 'Pausando' : 'Reactivando', 'producto:', product.id);
                      // TODO: Implementar cambio de estado
                    }}>
                      {product.status === 'active' ? (
                        <>
                          <Pause className="mr-2 h-4 w-4" />
                          Pausar anuncio
                        </>
                      ) : (
                        <>
                          <Play className="mr-2 h-4 w-4" />
                          Reactivar anuncio
                        </>
                      )}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      className="text-destructive"
                      onClick={() => {
                        console.log('Eliminando producto:', product.id);
                        if (confirm('¿Estás seguro de que quieres eliminar este producto?')) {
                          // TODO: Implementar eliminación
                        }
                      }}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Eliminar
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
};