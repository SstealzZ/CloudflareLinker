import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from './ui/button';

/**
 * Navigation bar component
 * 
 * @returns {JSX.Element} - Navigation bar component
 */
const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  
  /**
   * Check if a path is active
   * 
   * @param {string} path - Path to check
   * @returns {boolean} - Whether the path is active
   */
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // Don't show navbar on setup page
  if (location.pathname === '/setup') {
    return null;
  }
  
  return (
    <nav className="bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-xl nav-brand">
                Cloudflare Linker
              </Link>
            </div>
            
            {isAuthenticated() && (
              <div className="ml-10 flex items-center space-x-4">
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/dashboard')
                      ? 'bg-primary text-primary-foreground'
                      : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  Tableau de bord
                </Link>
                <Link
                  to="/dns"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/dns')
                      ? 'bg-primary text-primary-foreground'
                      : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  DNS
                </Link>
                <Link
                  to="/logs"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/logs')
                      ? 'bg-primary text-primary-foreground'
                      : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  Logs
                </Link>
              </div>
            )}
          </div>
          
          <div className="flex items-center">
            {!isAuthenticated() ? (
              <Link to="/login">
                <Button variant="outline">Se connecter</Button>
              </Link>
            ) : (
              <Button onClick={handleLogout} variant="default">
                Déconnexion
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 