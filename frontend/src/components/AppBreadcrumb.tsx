import { 
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { useRealtimeUpdates } from "@/hooks/useWebSocket";
import { Badge } from "@/components/ui/badge";
import { Wifi, WifiOff } from "lucide-react";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface AppBreadcrumbProps {
  items: BreadcrumbItem[];
}

export function AppBreadcrumb({ items }: AppBreadcrumbProps) {
  const { isConnected, error, reconnectCount } = useRealtimeUpdates();

  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      <div className="flex items-center gap-2 flex-1">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        
        <Breadcrumb>
          <BreadcrumbList>
            {items.map((item, index) => (
              <div key={item.label} className="flex items-center">
                {index > 0 && <BreadcrumbSeparator className="hidden md:block" />}
                <BreadcrumbItem>
                  {item.href ? (
                    <BreadcrumbLink href={item.href}>
                      {item.label}
                    </BreadcrumbLink>
                  ) : (
                    <BreadcrumbPage>{item.label}</BreadcrumbPage>
                  )}
                </BreadcrumbItem>
              </div>
            ))}
          </BreadcrumbList>
        </Breadcrumb>
      </div>
      
      {/* Connection Status */}
      <div className="flex items-center gap-2">
        {isConnected ? (
          <Badge variant="default" className="bg-green-500 text-white">
            <Wifi className="w-3 h-3 mr-1" />
            <span className="hidden sm:inline">Conectado</span>
          </Badge>
        ) : (
          <Badge variant="destructive">
            <WifiOff className="w-3 h-3 mr-1" />
            <span className="hidden sm:inline">{error ? 'Error' : 'Desconectado'}</span>
          </Badge>
        )}
        {reconnectCount > 0 && (
          <span className="text-xs text-muted-foreground hidden md:inline">
            Reintentando... ({reconnectCount})
          </span>
        )}
      </div>
    </header>
  );
}