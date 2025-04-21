import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card';
import Button from '../components/ui/button';
import Input from '../components/ui/input';
import { useAuth } from '../context/AuthContext';

/**
 * Login page component
 * 
 * @returns {JSX.Element} - Login page component
 */
const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
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
      [name]: value,
    }));
  };

  /**
   * Handle form submission
   * 
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('Veuillez entrer un nom d\'utilisateur et un mot de passe');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Identifiants incorrects');
      }
    } catch (err) {
      setError('Une erreur est survenue lors de la connexion');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] py-8">
      <Card className="w-full max-w-md glass">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Connexion</CardTitle>
          <CardDescription className="text-center">
            Connectez-vous à votre compte Cloudflare Linker
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4">
              {error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">
                  {error}
                </div>
              )}
              
              <div className="grid gap-2">
                <label htmlFor="username" className="text-sm font-medium">
                  Nom d'utilisateur
                </label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={loading}
                  required
                />
              </div>
              
              <div className="grid gap-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Mot de passe
                </label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={loading}
                  required
                />
              </div>
              
              <Button type="submit" disabled={loading} variant="gradient" className="w-full">
                {loading ? 'Connexion en cours...' : 'Se connecter'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginPage; 