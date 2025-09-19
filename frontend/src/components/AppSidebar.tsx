import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { 
  Bot, 
  BarChart3, 
  Package, 
  MessageSquare, 
  Settings, 
  Search,
  Activity,
  TrendingUp,
  Bell,
  HelpCircle
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useMetrics, useProducts, useAutoDetectionStatus } from "@/hooks/useAPI";

export function AppSidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { data: metrics } = useMetrics();
  const { data: products } = useProducts();
  const { data: autoDetection } = useAutoDetectionStatus();

  const activeProducts = products?.filter(p => p.status === 'active').length || 0;
  const pendingMessages = Math.floor((metrics?.msg_rate || 0) * 0.3); // Mock pending messages

  const menuItems = [
    {
      title: "Dashboard",
      icon: BarChart3,
      url: "/",
      badge: null,
      active: location.pathname === "/",
    },
    {
      title: "Productos",
      icon: Package,
      url: "/products",
      badge: activeProducts > 0 ? activeProducts.toString() : null,
      active: location.pathname === "/products",
    },
    {
      title: "Mensajes",
      icon: MessageSquare,
      url: "/messages",
      badge: pendingMessages > 0 ? pendingMessages.toString() : null,
      badgeVariant: "destructive" as const,
      active: location.pathname === "/messages",
    },
    {
      title: "Auto-detección",
      icon: Search,
      url: "/detection",
      badge: autoDetection?.is_running ? "ON" : "OFF",
      badgeVariant: autoDetection?.is_running ? "default" : "secondary" as const,
      active: location.pathname === "/detection",
    },
    {
      title: "Analíticas",
      icon: TrendingUp,
      url: "/analytics",
      badge: null,
      active: location.pathname === "/analytics",
    },
    {
      title: "Notificaciones",
      icon: Bell,
      url: "/notifications",
      badge: "3",
      badgeVariant: "secondary" as const,
      active: location.pathname === "/notifications",
    },
  ];

  const bottomItems = [
    {
      title: "Configuración",
      icon: Settings,
      url: "/settings",
    },
    {
      title: "Ayuda",
      icon: HelpCircle,
      url: "/help",
    },
  ];

  return (
    <Sidebar>
      <SidebarHeader className="border-b">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-primary-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="font-semibold text-sm truncate">Wall-E Research</h2>
            <p className="text-xs text-muted-foreground">Dashboard Control</p>
          </div>
          <div className="flex items-center">
            {metrics?.success_rate !== undefined && (
              <Badge variant="outline" className="text-xs">
                <Activity className="w-3 h-3 mr-1" />
                {Math.round(metrics.success_rate)}%
              </Badge>
            )}
          </div>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarMenu>
          {menuItems.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton 
                className={`w-full justify-start ${item.active ? 'bg-accent text-accent-foreground' : ''}`}
                onClick={() => {
                  navigate(item.url);
                }}
              >
                <item.icon className="w-4 h-4" />
                <span className="flex-1">{item.title}</span>
                {item.badge && (
                  <Badge 
                    variant={item.badgeVariant || "default"} 
                    className="ml-auto text-xs"
                  >
                    {item.badge}
                  </Badge>
                )}
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="border-t">
        <SidebarMenu>
          {bottomItems.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton
                onClick={() => {
                  if (item.url) {
                    navigate(item.url);
                  } else {
                    console.log('Opening:', item.title);
                  }
                }}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.title}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
        
        <div className="px-3 py-2 text-xs text-muted-foreground">
          <div className="flex items-center justify-between">
            <span>Sistema activo</span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Online</span>
            </div>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}