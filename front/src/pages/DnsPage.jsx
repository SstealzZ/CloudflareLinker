import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import Button from '../components/ui/button';
import { getDnsRecords, createDnsRecord, updateAllDnsRecordIps } from '../api/dns';
import DnsRecordCard from '../components/DnsRecordCard';
import DnsRecordForm from '../components/DnsRecordForm';

/**
 * DNS management page component
 * 
 * @returns {JSX.Element} - DNS page component
 */
const DnsPage = () => {
  const [dnsRecords, setDnsRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [updatingAllIps, setUpdatingAllIps] = useState(false);

  /**
   * Fetch DNS records
   */
  const fetchRecords = async () => {
    try {
      setLoading(true);
      const records = await getDnsRecords();
      setDnsRecords(records);
    } catch (error) {
      console.error('Error fetching DNS records:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load data on component mount
  useEffect(() => {
    fetchRecords();
  }, []);

  /**
   * Handle form submission
   * 
   * @param {Object} recordData - DNS record data
   */
  const handleCreateRecord = async (recordData) => {
    try {
      setLoading(true);
      await createDnsRecord(recordData);
      setShowForm(false);
      await fetchRecords();
    } catch (error) {
      console.error('Error creating DNS record:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle record update or deletion
   */
  const handleRecordChange = async () => {
    await fetchRecords();
  };

  /**
   * Handle updating all IP addresses
   */
  const handleUpdateAllIps = async () => {
    try {
      setUpdatingAllIps(true);
      await updateAllDnsRecordIps();
      await fetchRecords();
    } catch (error) {
      console.error('Error updating all IPs:', error);
    } finally {
      setUpdatingAllIps(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Gestion des DNS</h1>
          <p className="text-muted-foreground">
            Gérez vos enregistrements DNS Cloudflare
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-3">
          <Button 
            variant="outline" 
            onClick={handleUpdateAllIps}
            disabled={updatingAllIps || loading}
            className="text-white border-white hover:bg-primary/20"
          >
            {updatingAllIps ? 'Mise à jour...' : 'Update all IP'}
          </Button>
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Annuler' : 'Ajouter un enregistrement'}
          </Button>
        </div>
      </div>

      {showForm && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Nouvel enregistrement DNS</CardTitle>
          </CardHeader>
          <CardContent>
            <DnsRecordForm onSubmit={handleCreateRecord} onCancel={() => setShowForm(false)} />
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="animate-pulse text-muted-foreground">Chargement...</div>
        </div>
      ) : dnsRecords.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dnsRecords.map((record) => (
            <DnsRecordCard
              key={record.id}
              record={record}
              onUpdate={handleRecordChange}
              onDelete={handleRecordChange}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-xl text-muted-foreground mb-4">
            Vous n'avez pas encore d'enregistrements DNS
          </p>
          {!showForm && (
            <Button onClick={() => setShowForm(true)}>
              Ajouter votre premier enregistrement
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default DnsPage; 