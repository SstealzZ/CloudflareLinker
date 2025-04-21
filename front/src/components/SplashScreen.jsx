import React from 'react';

/**
 * Splash screen component shown during app initialization
 * 
 * @param {Object} props - Component props
 * @param {boolean} [props.loading=true] - Whether loading is in progress
 * @param {string} [props.message='Chargement...'] - Message to display
 * @returns {JSX.Element} - SplashScreen component
 */
const SplashScreen = ({ loading = true, message = 'Chargement...' }) => {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center min-h-screen bg-background dark z-50">
      <div className="relative mb-8">
        <div className="w-16 h-16 md:w-24 md:h-24 border-t-2 border-b-2 border-primary rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 md:w-20 md:h-20 bg-background dark:bg-background rounded-full flex items-center justify-center">
            <span className="text-xl md:text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-600">
              CF
            </span>
          </div>
        </div>
      </div>
      
      <h1 className="text-3xl md:text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-600">
        Cloudflare Linker
      </h1>
      
      <div className="mt-4 text-muted-foreground">
        {loading && (
          <div className="flex items-center space-x-2">
            <span className="animate-pulse">{message}</span>
          </div>
        )}
      </div>
      
      <div className="glass px-4 py-2 mt-8 rounded-lg text-xs text-muted-foreground">
        Sécurisez et automatisez la gestion de vos DNS
      </div>
    </div>
  );
};

export default SplashScreen; 