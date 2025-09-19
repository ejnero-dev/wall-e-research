import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { AppBreadcrumb } from "@/components/AppBreadcrumb";
import { Separator } from "@/components/ui/separator";
import { AutoDetectionPanel } from "@/components/AutoDetectionPanel";

export default function Detection() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <AppBreadcrumb items={[{ label: "Dashboard", href: "/" }, { label: "Auto-detección" }]} />
          </div>
        </header>
        <Separator />
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="grid auto-rows-min gap-4 md:grid-cols-1">
            <div className="min-h-[100vh] flex-1 rounded-xl md:min-h-min">
              <AutoDetectionPanel />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}