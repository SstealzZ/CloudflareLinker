import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card';
import Button from '../components/ui/button';
import Input from '../components/ui/input';
import { useAuth } from '../context/AuthContext';
import { performSetup } from '../api/auth';

/**
 * Setup page component for first-time application configuration
 * 
 * @returns {JSX.Element} - Setup page component
 */
const SetupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    cloudflare_api_key: '',
    is_token: true
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [setupComplete, setSetupComplete] = useState(false);
  const { loginWithToken, isAuthenticated, fetchUser } = useAuth();
  const navigate = useNavigate();

  /**
   * Handle input changes
   * 
   * @param {Event} e - Input change event
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Effect to redirect after setup is complete
   */
  useEffect(() => {
    let redirectTimer;
    
    if (setupComplete) {
      console.log('Configuration terminée, redirection en cours...');
      redirectTimer = setTimeout(() => {
        console.log('Redirection vers le dashboard après le délai');
        navigate('/dashboard', { replace: true });
      }, 2000);
    }
    
    return () => {
      if (redirectTimer) clearTimeout(redirectTimer);
    };
  }, [setupComplete, navigate]);

  /**
   * Handle form submission
   * 
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.username || !formData.email || !formData.password || 
        !formData.cloudflare_api_key) {
      setError('Veuillez remplir tous les champs requis');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      console.log('Envoi des données de configuration...');
      
      // Perform setup
      const setupResult = await performSetup(formData);
      console.log('Résultat de la configuration:', setupResult);
      
      if (setupResult.success) {
        // Get token from response
        const token = setupResult.data.access_token;
        console.log('Token reçu:', token?.substring(0, 10) + '...');
        
        try {
          // Login with token
          console.log('Connexion directe avec le token...');
          const loginResult = await loginWithToken(token);
          
          if (loginResult.success) {
            console.log('Authentification avec token réussie');
            setSetupComplete(true);
            
            // Force immediate redirect
            console.log('Redirection vers le dashboard'); 
            setTimeout(() => {
              navigate('/dashboard', { replace: true });
            }, 1500);
          } else {
            setError('Problème d\'authentification après la configuration');
            console.error('Échec de l\'authentification après configuration');
          }
        } catch (loginErr) {
          console.error('Erreur lors de la connexion avec token:', loginErr);
          setError('Erreur lors de la connexion après configuration');
        }
      } else {
        setError(setupResult.error || 'Une erreur est survenue lors de la configuration');
        console.error('Échec de la configuration:', setupResult.error);
      }
    } catch (err) {
      setError('Une erreur est survenue lors de la configuration');
      console.error('Exception lors de la configuration:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Configuration initiale</CardTitle>
          <CardDescription>
            Configurez votre compte administrateur pour Cloudflare Linker
          </CardDescription>
        </CardHeader>
        
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="bg-red-500/10 text-red-500 p-3 rounded-md text-sm">
                {error}
              </div>
            )}
            
            {setupComplete && (
              <div className="bg-green-500/10 text-green-500 p-3 rounded-md text-sm">
                Configuration réussie ! Redirection vers le tableau de bord...
              </div>
            )}
            
            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium">
                Nom d'utilisateur
              </label>
              <Input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                placeholder="admin"
                required
                disabled={loading || setupComplete}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="admin@example.com"
                required
                disabled={loading || setupComplete}
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Mot de passe
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="********"
                required
                disabled={loading || setupComplete}
              />
              <p className="text-xs text-muted-foreground">
                Le mot de passe doit contenir au moins 8 caractères
              </p>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="cloudflare_api_key" className="text-sm font-medium">
                Jeton API Cloudflare
              </label>
              <Input
                id="cloudflare_api_key"
                name="cloudflare_api_key"
                type="password"
                value={formData.cloudflare_api_key}
                onChange={handleChange}
                placeholder="Votre jeton API Cloudflare"
                required
                disabled={loading || setupComplete}
              />
            </div>
          </CardContent>
          
          <CardFooter>
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading || setupComplete}
            >
              {loading ? 'Configuration en cours...' : (setupComplete ? 'Configuration terminée' : 'Configurer')}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

export default SetupPage; 