import React, { createContext, useContext, useEffect, useState } from 'react';
import { toast } from '@/hooks/use-toast';

interface AccessibilityContextType {
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: 'small' | 'normal' | 'large';
  focusIndicators: boolean;
  announcements: boolean;
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  setFontSize: (size: 'small' | 'normal' | 'large') => void;
  toggleFocusIndicators: () => void;
  toggleAnnouncements: () => void;
  announceToScreenReader: (message: string) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  // Estado de las preferencias de accesibilidad
  const [reducedMotion, setReducedMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState<'small' | 'normal' | 'large'>('normal');
  const [focusIndicators, setFocusIndicators] = useState(true);
  const [announcements, setAnnouncements] = useState(true);

  // Detectar preferencias del sistema al montar
  useEffect(() => {
    // Detectar reducción de movimiento preferida por el usuario
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    setReducedMotion(prefersReducedMotion);

    // Detectar alto contraste
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
    setHighContrast(prefersHighContrast);

    // Cargar preferencias guardadas
    const savedPreferences = localStorage.getItem('wall-e-accessibility');
    if (savedPreferences) {
      try {
        const prefs = JSON.parse(savedPreferences);
        setReducedMotion(prefs.reducedMotion ?? prefersReducedMotion);
        setHighContrast(prefs.highContrast ?? prefersHighContrast);
        setFontSize(prefs.fontSize ?? 'normal');
        setFocusIndicators(prefs.focusIndicators ?? true);
        setAnnouncements(prefs.announcements ?? true);
      } catch (error) {
        console.error('Error loading accessibility preferences:', error);
      }
    }

    // Listener para cambios en las preferencias del sistema
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleMotionChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches);
    };
    mediaQuery.addEventListener('change', handleMotionChange);

    const contrastQuery = window.matchMedia('(prefers-contrast: high)');
    const handleContrastChange = (e: MediaQueryListEvent) => {
      setHighContrast(e.matches);
    };
    contrastQuery.addEventListener('change', handleContrastChange);

    return () => {
      mediaQuery.removeEventListener('change', handleMotionChange);
      contrastQuery.removeEventListener('change', handleContrastChange);
    };
  }, []);

  // Aplicar clases CSS basadas en las preferencias
  useEffect(() => {
    const root = document.documentElement;
    
    // Aplicar reducción de movimiento
    if (reducedMotion) {
      root.classList.add('reduce-motion');
    } else {
      root.classList.remove('reduce-motion');
    }

    // Aplicar alto contraste
    if (highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    // Aplicar tamaño de fuente
    root.classList.remove('font-small', 'font-normal', 'font-large');
    root.classList.add(`font-${fontSize}`);

    // Aplicar indicadores de foco
    if (focusIndicators) {
      root.classList.add('focus-indicators');
    } else {
      root.classList.remove('focus-indicators');
    }

    // Guardar preferencias
    const preferences = {
      reducedMotion,
      highContrast,
      fontSize,
      focusIndicators,
      announcements,
    };
    localStorage.setItem('wall-e-accessibility', JSON.stringify(preferences));
  }, [reducedMotion, highContrast, fontSize, focusIndicators, announcements]);

  // Funciones para alternar preferencias
  const toggleReducedMotion = () => {
    setReducedMotion(!reducedMotion);
    toast({
      title: 'Configuración de accesibilidad',
      description: `Movimiento reducido ${!reducedMotion ? 'activado' : 'desactivado'}`,
    });
  };

  const toggleHighContrast = () => {
    setHighContrast(!highContrast);
    toast({
      title: 'Configuración de accesibilidad',
      description: `Alto contraste ${!highContrast ? 'activado' : 'desactivado'}`,
    });
  };

  const handleSetFontSize = (size: 'small' | 'normal' | 'large') => {
    setFontSize(size);
    toast({
      title: 'Configuración de accesibilidad',
      description: `Tamaño de fuente cambiado a ${size === 'small' ? 'pequeño' : size === 'large' ? 'grande' : 'normal'}`,
    });
  };

  const toggleFocusIndicators = () => {
    setFocusIndicators(!focusIndicators);
    toast({
      title: 'Configuración de accesibilidad',
      description: `Indicadores de foco ${!focusIndicators ? 'activados' : 'desactivados'}`,
    });
  };

  const toggleAnnouncements = () => {
    setAnnouncements(!announcements);
    toast({
      title: 'Configuración de accesibilidad',
      description: `Anuncios de pantalla ${!announcements ? 'activados' : 'desactivados'}`,
    });
  };

  // Función para anunciar mensajes a lectores de pantalla
  const announceToScreenReader = (message: string) => {
    if (!announcements) return;

    // Crear elemento ARIA live para anuncios
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remover después de que se haya anunciado
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  const value: AccessibilityContextType = {
    reducedMotion,
    highContrast,
    fontSize,
    focusIndicators,
    announcements,
    toggleReducedMotion,
    toggleHighContrast,
    setFontSize: handleSetFontSize,
    toggleFocusIndicators,
    toggleAnnouncements,
    announceToScreenReader,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {/* Screen reader announcements container */}
      <div 
        id="sr-announcements" 
        aria-live="polite" 
        aria-atomic="true" 
        className="sr-only"
      />
      
      {/* Skip navigation link for keyboard users */}
      <a 
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:border-2 focus:border-primary-foreground"
      >
        Saltar al contenido principal
      </a>
      
      {children}
    </AccessibilityContext.Provider>
  );
};

// Componente de configuración de accesibilidad
export const AccessibilitySettings = () => {
  const {
    reducedMotion,
    highContrast,
    fontSize,
    focusIndicators,
    announcements,
    toggleReducedMotion,
    toggleHighContrast,
    setFontSize,
    toggleFocusIndicators,
    toggleAnnouncements,
  } = useAccessibility();

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Configuración de Accesibilidad</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Personaliza la interfaz para mejorar tu experiencia de uso.
        </p>
      </div>

      <div className="space-y-4">
        {/* Reducción de movimiento */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <h4 className="font-medium">Reducir movimiento</h4>
            <p className="text-sm text-muted-foreground">
              Minimiza animaciones y transiciones
            </p>
          </div>
          <button
            onClick={toggleReducedMotion}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
              reducedMotion ? 'bg-primary' : 'bg-gray-200'
            }`}
            role="switch"
            aria-checked={reducedMotion}
            aria-labelledby="reduce-motion-label"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                reducedMotion ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Alto contraste */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <h4 className="font-medium">Alto contraste</h4>
            <p className="text-sm text-muted-foreground">
              Aumenta el contraste para mejor visibilidad
            </p>
          </div>
          <button
            onClick={toggleHighContrast}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
              highContrast ? 'bg-primary' : 'bg-gray-200'
            }`}
            role="switch"
            aria-checked={highContrast}
            aria-labelledby="high-contrast-label"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                highContrast ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Tamaño de fuente */}
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2">Tamaño de fuente</h4>
          <p className="text-sm text-muted-foreground mb-3">
            Ajusta el tamaño del texto en toda la aplicación
          </p>
          <div className="flex gap-2">
            {(['small', 'normal', 'large'] as const).map((size) => (
              <button
                key={size}
                onClick={() => setFontSize(size)}
                className={`px-3 py-2 rounded-md border transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                  fontSize === size
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-background border-border hover:bg-accent'
                }`}
                aria-pressed={fontSize === size}
              >
                {size === 'small' ? 'Pequeño' : size === 'large' ? 'Grande' : 'Normal'}
              </button>
            ))}
          </div>
        </div>

        {/* Indicadores de foco */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <h4 className="font-medium">Indicadores de foco</h4>
            <p className="text-sm text-muted-foreground">
              Resalta elementos activos para navegación por teclado
            </p>
          </div>
          <button
            onClick={toggleFocusIndicators}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
              focusIndicators ? 'bg-primary' : 'bg-gray-200'
            }`}
            role="switch"
            aria-checked={focusIndicators}
            aria-labelledby="focus-indicators-label"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                focusIndicators ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Anuncios de pantalla */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <h4 className="font-medium">Anuncios de pantalla</h4>
            <p className="text-sm text-muted-foreground">
              Habilita notificaciones para lectores de pantalla
            </p>
          </div>
          <button
            onClick={toggleAnnouncements}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
              announcements ? 'bg-primary' : 'bg-gray-200'
            }`}
            role="switch"
            aria-checked={announcements}
            aria-labelledby="announcements-label"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                announcements ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
};