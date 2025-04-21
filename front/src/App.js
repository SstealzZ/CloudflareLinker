import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DnsPage from './pages/DnsPage';
import LogsPage from './pages/LogsPage';
import SetupPage from './pages/SetupPage';
import SplashScreen from './components/SplashScreen';
import { checkSetupStatus } from './api/auth';
import './index.css';

/**
 * Route that requires authentication
 * 
 * @param {Object} props - Component props
 * @param {JSX.Element} props.children - Child component to render if authenticated
 * @returns {JSX.Element} - Protected route
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <SplashScreen message="Vérification de l'authentification..." />;
  }
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

/**
 * Route only accessible when not authenticated
 * 
 * @param {Object} props - Component props
 * @param {JSX.Element} props.children - Child component to render if not authenticated
 * @returns {JSX.Element} - Anonymous route
 */
const AnonymousRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <SplashScreen message="Vérification de l'authentification..." />;
  }
  
  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

/**
 * Main application component
 * 
 * @returns {JSX.Element} - App component
 */
function App() {
  const [loading, setLoading] = useState(true);
  const [needsSetup, setNeedsSetup] = useState(false);
  const [initializing, setInitializing] = useState(true);

  // Check if application needs setup on mount
  useEffect(() => {
    const checkSetup = async () => {
      try {
        console.log('Vérification du statut de configuration...');
        const setupRequired = await checkSetupStatus();
        console.log('Configuration requise:', setupRequired);
        setNeedsSetup(setupRequired);
      } catch (error) {
        console.error('Error checking setup status:', error);
      } finally {
        setLoading(false);
        // Give the splash screen a minimum time to show
        setTimeout(() => {
          setInitializing(false);
        }, 1500);
      }
    };

    checkSetup();
  }, []);

  if (loading || initializing) {
    return <SplashScreen message={loading ? "Initialisation..." : "Démarrage de l'application..."} />;
  }

  /**
   * Application routing
   */
  const AppRoutes = () => {
    const { isAuthenticated } = useAuth();

    return (
      <Routes>
        <Route 
          path="/" 
          element={
            needsSetup ? 
            <Navigate to="/setup" replace /> : 
            <LandingPage />
          }
        />
        <Route 
          path="/setup" 
          element={
            needsSetup ? 
            <SetupPage /> : 
            <Navigate to={isAuthenticated() ? "/dashboard" : "/login"} replace />
          }
        />
        <Route 
          path="/login" 
          element={
            needsSetup ? 
            <Navigate to="/setup" replace /> : 
            <AnonymousRoute>
              <LoginPage />
            </AnonymousRoute>
          }
        />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/dns" 
          element={
            <ProtectedRoute>
              <DnsPage />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/logs" 
          element={
            <ProtectedRoute>
              <LogsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    );
  };

  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-background dark">
          <Navbar />
          <AppRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

/**
 * Landing page component
 * 
 * @returns {JSX.Element} - Landing page component
 */
const LandingPage = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center p-4">
      <h1 className="text-4xl md:text-6xl font-bold mb-6">Cloudflare Linker</h1>
      <p className="text-xl md:text-2xl mb-8 max-w-3xl text-muted-foreground">
        Automatisez la gestion de vos DNS Cloudflare, même avec des IPs dynamiques
      </p>
      
      {isAuthenticated() ? (
        <Navigate to="/dashboard" replace />
      ) : (
        <Navigate to="/login" replace />
      )}
    </div>
  );
};

export default App; 