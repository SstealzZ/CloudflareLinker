import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import Button from '../components/ui/button';
import { getUserLogs, getSystemLogs } from '../api/logs';
import LogItem from '../components/LogItem';

/**
 * Logs page component
 * 
 * @returns {JSX.Element} - Logs page component
 */
const LogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [loading, setLoading] = useState({
    user: true,
    system: true,
  });
  const [showSystemLogs, setShowSystemLogs] = useState(false);

  /**
   * Fetch user logs
   */
  const fetchUserLogs = async () => {
    try {
      setLoading(prev => ({ ...prev, user: true }));
      const logsData = await getUserLogs(0, 100);
      setLogs(logsData);
    } catch (error) {
      console.error('Error fetching user logs:', error);
    } finally {
      setLoading(prev => ({ ...prev, user: false }));
    }
  };

  /**
   * Fetch system logs
   */
  const fetchSystemLogs = async () => {
    try {
      setLoading(prev => ({ ...prev, system: true }));
      const logsData = await getSystemLogs(0, 100);
      setSystemLogs(logsData);
    } catch (error) {
      console.error('Error fetching system logs:', error);
    } finally {
      setLoading(prev => ({ ...prev, system: false }));
    }
  };

  // Load data on component mount and when view changes
  useEffect(() => {
    if (showSystemLogs) {
      fetchSystemLogs();
    } else {
      fetchUserLogs();
    }
  }, [showSystemLogs]);

  /**
   * Get the badge color for each log level
   */
  const getLevelCounts = (logsData) => {
    const counts = {
      INFO: 0,
      WARNING: 0,
      ERROR: 0,
      SUCCESS: 0
    };
    
    logsData.forEach(log => {
      if (counts[log.level] !== undefined) {
        counts[log.level]++;
      }
    });
    
    return counts;
  };

  const currentLogs = showSystemLogs ? systemLogs : logs;
  const levelCounts = getLevelCounts(currentLogs);

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Journaux d'activité</h1>
          <p className="text-muted-foreground">
            Consultez l'historique des actions sur votre compte
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Button 
            variant="outline" 
            onClick={() => setShowSystemLogs(!showSystemLogs)}
            className="text-white border-white hover:bg-primary/20"
          >
            {showSystemLogs ? 'Voir mes activités' : 'Voir les logs système'}
          </Button>
        </div>
      </div>

      {/* Log summary badges */}
      <div className="flex flex-wrap gap-3 mb-4">
        <div className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full text-xs">
          Informations: {levelCounts.INFO}
        </div>
        <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full text-xs">
          Succès: {levelCounts.SUCCESS}
        </div>
        <div className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-xs">
          Avertissements: {levelCounts.WARNING}
        </div>
        <div className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full text-xs">
          Erreurs: {levelCounts.ERROR}
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle>{showSystemLogs ? 'Logs système' : 'Vos activités'}</CardTitle>
        </CardHeader>
        <CardContent>
          {loading[showSystemLogs ? 'system' : 'user'] ? (
            <div className="flex justify-center py-8">
              <div className="animate-pulse text-muted-foreground">Chargement...</div>
            </div>
          ) : currentLogs.length > 0 ? (
            <div className="space-y-2">
              {currentLogs.map((log) => (
                <LogItem key={log.id} log={log} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                Aucune activité enregistrée
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default LogsPage; 