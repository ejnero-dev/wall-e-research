import { ActiveListings } from "@/components/ActiveListings";
import { AutomatedResponses } from "@/components/AutomatedResponses";
import { QuickStats } from "@/components/QuickStats";
import { AutoDetectionPanel } from "@/components/AutoDetectionPanel";
import { AppSidebar } from "@/components/AppSidebar";
import { AppBreadcrumb } from "@/components/AppBreadcrumb";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";

const Index = () => {
  const breadcrumbItems = [
    { label: "Dashboard", href: "#" },
    { label: "Panel Principal" },
  ];

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <AppBreadcrumb items={breadcrumbItems} />
        
        {/* Main Content */}
        <div className="flex flex-1 flex-col gap-6 p-6">
          {/* Hero Section */}
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">Vista General del Sistema</h2>
            <p className="text-muted-foreground">
              Monitoreo en tiempo real de tu sistema de automatización Wall-E. Gestiona productos, conversaciones y análisis desde un solo lugar.
            </p>
          </div>
          
          {/* Quick Stats Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Métricas en Tiempo Real</h3>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Última actualización: hace {new Date().getSeconds()}s</span>
              </div>
            </div>
            <QuickStats />
          </div>
          
          {/* Dashboard Grid */}
          <div className="grid gap-6 xl:grid-cols-3">
            <div className="xl:col-span-2 space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Gestión de Productos y Conversaciones</h3>
                <div className="grid gap-6 lg:grid-cols-2">
                  <ActiveListings />
                  <AutomatedResponses />
                </div>
              </div>
            </div>
            
            <div className="xl:col-span-1 space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Automatización Inteligente</h3>
                <AutoDetectionPanel />
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
};

export default Index;