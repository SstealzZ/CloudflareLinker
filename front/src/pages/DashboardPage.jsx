import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardLogs } from '../components/ui/card';
import Button from '../components/ui/button';
import { useAuth } from '../context/AuthContext';
import { getDnsRecords } from '../api/dns';
import { getUserLogs } from '../api/logs';
import DnsRecordCard from '../components/DnsRecordCard';
import LogItem from '../components/LogItem';

/**
 * Dashboard page component
 * 
 * @returns {JSX.Element} - Dashboard page component
 */
const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [dnsRecords, setDnsRecords] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState({
    dns: true,
    logs: true
  });

  /**
   * Fetch DNS records
   */
  const fetchDnsRecords = async () => {
    try {
      setLoading(prev => ({ ...prev, dns: true }));
      const records = await getDnsRecords();
      setDnsRecords(records);
    } catch (error) {
      console.error('Error fetching DNS records:', error);
    } finally {
      setLoading(prev => ({ ...prev, dns: false }));
    }
  };

  /**
   * Fetch recent logs
   */
  const fetchRecentLogs = async () => {
    try {
      setLoading(prev => ({ ...prev, logs: true }));
      const logsData = await getUserLogs(0, 5);
      setLogs(logsData);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(prev => ({ ...prev, logs: false }));
    }
  };

  /**
   * Navigate to logs page
   */
  const handleViewAllLogs = () => {
    navigate('/logs');
  };

  /**
   * Navigate to DNS page
   */
  const handleAddDns = () => {
    navigate('/dns');
  };

  // Load data on component mount
  useEffect(() => {
    fetchDnsRecords();
    fetchRecentLogs();
  }, []);

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Tableau de bord</h1>
          <p className="text-muted-foreground">
            Bienvenue {user?.username || ''} sur votre tableau de bord Cloudflare Linker
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Vos enregistrements DNS</CardTitle>
              <Button onClick={handleAddDns}>Gérer les DNS</Button>
            </CardHeader>
            <CardContent>
              {loading.dns ? (
                <div className="flex justify-center py-12">
                  <div className="animate-pulse text-muted-foreground">Chargement...</div>
                </div>
              ) : dnsRecords.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {dnsRecords.slice(0, 4).map((record) => (
                    <DnsRecordCard
                      key={record.id}
                      record={record}
                      onUpdate={fetchDnsRecords}
                      onDelete={fetchDnsRecords}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-muted-foreground mb-4">
                    Vous n'avez pas encore d'enregistrements DNS
                  </p>
                  <Button onClick={handleAddDns}>
                    Ajouter votre premier enregistrement
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <CardLogs 
            title="Activité récente" 
            onViewAll={handleViewAllLogs}
          >
            {loading.logs ? (
              <div className="flex justify-center py-8">
                <div className="animate-pulse text-muted-foreground">Chargement...</div>
              </div>
            ) : logs.length > 0 ? (
              <div className="space-y-2 max-h-[500px] overflow-auto pr-2">
                {logs.map((log) => (
                  <LogItem key={log.id} log={log} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">
                  Aucune activité récente
                </p>
              </div>
            )}
          </CardLogs>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;