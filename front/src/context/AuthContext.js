import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

/**
 * Authentication context for managing user authentication state
 */
const AuthContext = createContext(null);

/**
 * API URL from environment or default
 */
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * AuthProvider component for wrapping the application with authentication context
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Check if user is authenticated
   * 
   * @returns {boolean} - Whether the user is authenticated
   */
  const isAuthenticated = useCallback(() => {
    const currentToken = localStorage.getItem('token');
    return !!currentToken;
  }, []);

  /**
   * Set up axios interceptor for authentication
   */
  useEffect(() => {
    // Apply token to all axios requests
    axios.defaults.headers.common['Authorization'] = token ? `Bearer ${token}` : '';
    
    const interceptor = axios.interceptors.request.use(
      config => {
        const currentToken = localStorage.getItem('token');
        if (currentToken) {
          config.headers.Authorization = `Bearer ${currentToken}`;
        }
        return config;
      },
      error => Promise.reject(error)
    );
    
    return () => {
      axios.interceptors.request.eject(interceptor);
    };
  }, [token]);

  /**
   * Get user profile
   */
  const fetchUser = useCallback(async () => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      setLoading(false);
      return;
    }
    
    try {
      console.log('Récupération du profil utilisateur avec le token:', currentToken.substring(0, 10) + '...');
      const response = await axios.get(`${API_URL}/auth/me`);
      setUser(response.data);
      console.log('Profil utilisateur récupéré:', response.data);
      return true;
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      if (err.response?.status === 401) {
        console.log('Token invalide, déconnexion...');
        logout();
      }
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token, fetchUser]);

  /**
   * Force authentication status update
   */
  const updateAuthStatus = useCallback(() => {
    console.log('Mise à jour du statut d\'authentification');
    const storedToken = localStorage.getItem('token');
    if (storedToken && storedToken !== token) {
      setToken(storedToken);
      fetchUser();
    }
  }, [token, fetchUser]);

  /**
   * Login with username and password
   * 
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<{success: boolean, error?: string}>} - Login result
   */
  const login = async (username, password) => {
    try {
      setError(null);
      console.log('Tentative de connexion pour:', username);
      
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post(`${API_URL}/auth/login`, formData);
      console.log('Réponse du serveur:', response.data);
      
      const accessToken = response.data.access_token;
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
      
      // Forcer la récupération du profil
      await fetchUser();
      
      return { success: true };
    } catch (err) {
      console.error('Erreur de connexion:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to login';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    }
  };

  /**
   * Login with provided token
   *
   * @param {string} accessToken - Access token
   * @returns {Promise<{success: boolean, error?: string}>} - Login result
   */
  const loginWithToken = async (accessToken) => {
    try {
      console.log('Connexion avec token:', accessToken?.substring(0, 10) + '...');
      
      // Stocker le token dans localStorage ET dans l'état
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
      
      // Définir le token dans les headers par défaut d'Axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      
      // Forcer la récupération du profil
      const success = await fetchUser();
      
      console.log('Connexion avec token terminée, statut:', success ? 'succès' : 'échec');
      return { success };
    } catch (err) {
      console.error('Erreur de connexion avec token:', err);
      return { success: false, error: 'Failed to login with token' };
    }
  };

  /**
   * Logout current user
   */
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    sessionStorage.clear();
    setToken(null);
    setUser(null);
    
    // Reset any axios default headers
    delete axios.defaults.headers.common['Authorization'];
  }, []);

  const value = {
    user,
    token,
    loading,
    error,
    login,
    loginWithToken,
    logout,
    isAuthenticated,
    updateAuthStatus,
    fetchUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Hook for using the authentication context
 * 
 * @returns {Object} - Authentication context value
 */
export const useAuth = () => {
  return useContext(AuthContext);
}; 