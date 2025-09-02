import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export const StatsCardSkeleton = () => (
  <Card className="relative overflow-hidden">
    <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-primary/20 to-primary/10 animate-pulse" />
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <Skeleton className="h-4 w-24" />
      <div className="flex items-center gap-2">
        <Skeleton className="h-3 w-8" />
        <Skeleton className="h-4 w-4 rounded" />
      </div>
    </CardHeader>
    <CardContent className="space-y-3">
      <Skeleton className="h-8 w-16" />
      <div className="space-y-1">
        <Skeleton className="h-2 w-full" />
        <div className="flex justify-between">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-12" />
        </div>
      </div>
    </CardContent>
  </Card>
);

export const ProductCardSkeleton = () => (
  <div className="flex items-center gap-3 p-4 border rounded-lg animate-pulse">
    <Skeleton className="h-12 w-12 rounded-md" />
    <div className="flex-1 space-y-2">
      <div className="flex items-center gap-2">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
      <div className="flex items-center gap-3">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-3 w-16" />
      </div>
      <Skeleton className="h-3 w-24" />
    </div>
    <div className="flex items-center gap-4">
      <Skeleton className="h-4 w-8" />
      <Skeleton className="h-4 w-8" />
      <Skeleton className="h-8 w-8 rounded" />
    </div>
  </div>
);

export const DashboardLoadingSkeleton = () => (
  <div className="space-y-6 p-4">
    {/* Header skeleton */}
    <div className="space-y-2">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-96" />
    </div>
    
    {/* Stats grid skeleton */}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <StatsCardSkeleton key={i} />
      ))}
    </div>
    
    {/* Dashboard grid skeleton */}
    <div className="grid gap-6 xl:grid-cols-3">
      <div className="xl:col-span-2 space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Active Listings skeleton */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <Skeleton className="h-6 w-32" />
                <div className="flex gap-2">
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-8 w-20" />
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </CardContent>
          </Card>
          
          {/* Automated Responses skeleton */}
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-40" />
            </CardHeader>
            <CardContent className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="space-y-2 p-3 border rounded-lg">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-3/4" />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Auto Detection Panel skeleton */}
      <div className="xl:col-span-1">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-36" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-10 w-full" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-20 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
);

// Floating action loading state
export const FloatingActionLoader = ({ children }: { children: React.ReactNode }) => (
  <div className="relative">
    {children}
    <div className="absolute inset-0 bg-background/50 backdrop-blur-sm rounded-md flex items-center justify-center">
      <div className="flex items-center gap-2 text-sm">
        <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
        <span>Procesando...</span>
      </div>
    </div>
  </div>
);

// Shimmer effect for better loading experience
export const ShimmerWrapper = ({ children, isLoading }: { children: React.ReactNode; isLoading: boolean }) => (
  <div className={`${isLoading ? 'animate-pulse' : ''} transition-all duration-300`}>
    {children}
  </div>
);