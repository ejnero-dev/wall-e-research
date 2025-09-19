import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, Loader2 } from "lucide-react";
import { useAddProduct } from "@/hooks/useAPI";

interface ProductFormData {
  wallapop_url: string;
  auto_respond: boolean;
  ai_personality: string;
  response_delay_min: number;
  response_delay_max: number;
}

interface AddProductDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddProductDialog({ open, onOpenChange }: AddProductDialogProps) {
  const [formData, setFormData] = useState<ProductFormData>({
    wallapop_url: '',
    auto_respond: true,
    ai_personality: 'professional',
    response_delay_min: 15,
    response_delay_max: 60,
  });
  const [error, setError] = useState<string | null>(null);

  const addProduct = useAddProduct();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      // Basic URL validation
      if (!formData.wallapop_url) {
        throw new Error('Wallapop URL is required');
      }

      if (!formData.wallapop_url.includes('wallapop.com')) {
        throw new Error('Please enter a valid Wallapop URL');
      }

      await addProduct.mutateAsync(formData);
      onOpenChange(false);
      // Reset form
      setFormData({
        wallapop_url: '',
        auto_respond: true,
        ai_personality: 'professional',
        response_delay_min: 15,
        response_delay_max: 60,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add product');
    }
  };

  const handleInputChange = (field: keyof ProductFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const personalityOptions = [
    { value: 'professional', label: 'Professional', description: 'Formal and business-like' },
    { value: 'friendly', label: 'Friendly', description: 'Warm and approachable' },
    { value: 'casual', label: 'Casual', description: 'Relaxed and informal' },
    { value: 'enthusiastic', label: 'Enthusiastic', description: 'Energetic and positive' },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Agregar Nuevo Producto</DialogTitle>
          <DialogDescription>
            Añade un producto de Wallapop para gestionar automáticamente con Wall-E
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Wallapop URL */}
          <div className="space-y-2">
            <Label htmlFor="wallapop_url">URL de Wallapop *</Label>
            <Input
              id="wallapop_url"
              type="url"
              value={formData.wallapop_url}
              onChange={(e) => handleInputChange('wallapop_url', e.target.value)}
              placeholder="https://wallapop.com/item/..."
              required
            />
            <p className="text-sm text-muted-foreground">
              Pega la URL del producto de Wallapop. Wall-E extraerá automáticamente los detalles.
            </p>
          </div>

          {/* Auto-respond Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Respuesta Automática con IA</Label>
              <p className="text-sm text-muted-foreground">
                Permitir que Wall-E responda automáticamente a mensajes usando IA
              </p>
            </div>
            <Switch
              checked={formData.auto_respond}
              onCheckedChange={(checked) => handleInputChange('auto_respond', checked)}
            />
          </div>

          {/* AI Personality (only show if auto-respond is enabled) */}
          {formData.auto_respond && (
            <div className="space-y-3">
              <Label>Personalidad de la IA</Label>
              <RadioGroup
                value={formData.ai_personality}
                onValueChange={(value) => handleInputChange('ai_personality', value)}
                className="grid grid-cols-1 md:grid-cols-2 gap-4"
              >
                {personalityOptions.map((option) => (
                  <div key={option.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={option.value} id={option.value} />
                    <Card className="flex-1 cursor-pointer" onClick={() => handleInputChange('ai_personality', option.value)}>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">{option.label}</CardTitle>
                        <CardDescription className="text-xs">{option.description}</CardDescription>
                      </CardHeader>
                    </Card>
                  </div>
                ))}
              </RadioGroup>
            </div>
          )}

          {/* Response Delay (only show if auto-respond is enabled) */}
          {formData.auto_respond && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="response_delay_min">Retraso Mínimo (minutos)</Label>
                <Input
                  id="response_delay_min"
                  type="number"
                  min="1"
                  max="180"
                  value={formData.response_delay_min}
                  onChange={(e) => handleInputChange('response_delay_min', parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="response_delay_max">Retraso Máximo (minutos)</Label>
                <Input
                  id="response_delay_max"
                  type="number"
                  min="1"
                  max="180"
                  value={formData.response_delay_max}
                  onChange={(e) => handleInputChange('response_delay_max', parseInt(e.target.value))}
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              disabled={addProduct.isPending}
            >
              Cancelar
            </Button>
            <Button 
              type="submit" 
              disabled={addProduct.isPending}
            >
              {addProduct.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {addProduct.isPending ? 'Agregando...' : 'Agregar Producto'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}