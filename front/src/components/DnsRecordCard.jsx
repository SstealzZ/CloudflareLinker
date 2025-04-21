import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/card';
import Button from './ui/button';
import { formatDate } from '../lib/utils';
import { updateDnsRecordIp, deleteDnsRecord } from '../api/dns';

/**
 * Component to display a DNS record as a card
 * 
 * @param {Object} props - Component props
 * @param {Object} props.record - DNS record data
 * @param {Function} props.onUpdate - Callback when record is updated
 * @param {Function} props.onDelete - Callback when record is deleted
 * @returns {JSX.Element} - DNS record card component
 */
const DnsRecordCard = ({ record, onUpdate, onDelete }) => {
  const [loading, setLoading] = React.useState({
    updating: false,
    deleting: false
  });

  /**
   * Handle manual IP update
   */
  const handleUpdateIp = async () => {
    if (!record || loading.updating) return;

    try {
      setLoading(prev => ({ ...prev, updating: true }));
      await updateDnsRecordIp(record.id);
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error updating IP:', error);
    } finally {
      setLoading(prev => ({ ...prev, updating: false }));
    }
  };

  /**
   * Handle record deletion
   */
  const handleDelete = async () => {
    if (!record || loading.deleting) return;
    
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'enregistrement ${record.record_name} ?`)) {
      try {
        setLoading(prev => ({ ...prev, deleting: true }));
        await deleteDnsRecord(record.id);
        if (onDelete) onDelete();
      } catch (error) {
        console.error('Error deleting record:', error);
      } finally {
        setLoading(prev => ({ ...prev, deleting: false }));
      }
    }
  };

  /**
   * Get badge color based on record type
   */
  const getTypeColor = () => {
    switch (record.record_type) {
      case 'A':
        return 'bg-blue-600 text-white';
      case 'AAAA':
        return 'bg-purple-600 text-white';
      case 'CNAME':
        return 'bg-green-600 text-white';
      case 'TXT':
        return 'bg-yellow-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl truncate">{record.record_name}</CardTitle>
          <span className={`px-2 py-1 rounded-md text-xs font-medium ${getTypeColor()}`}>
            {record.record_type}
          </span>
        </div>
        <div className="text-xs text-muted-foreground">{record.zone_name}</div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Contenu:</span>
            <span className="text-sm truncate max-w-[200px]">{record.content}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Proxied:</span>
            <span className="text-sm">{record.proxied ? 'Oui' : 'Non'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Auto-update:</span>
            <span className="text-sm">{record.auto_update ? 'Activé' : 'Désactivé'}</span>
          </div>
          {record.last_updated_ip && (
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Dernière IP:</span>
              <span className="text-sm">{record.last_updated_ip}</span>
            </div>
          )}
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Dernière mise à jour:</span>
            <span className="text-sm">{record.updated_at ? formatDate(record.updated_at) : 'Jamais'}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between border-t pt-3">
        {record.record_type === 'A' || record.record_type === 'AAAA' ? (
          <Button 
            size="sm" 
            variant="secondary" 
            onClick={handleUpdateIp}
            disabled={loading.updating}
          >
            {loading.updating ? 'Mise à jour...' : 'Mettre à jour IP'}
          </Button>
        ) : (
          <div></div>
        )}
        <Button 
          size="sm" 
          variant="destructive" 
          onClick={handleDelete}
          disabled={loading.deleting}
        >
          {loading.deleting ? 'Suppression...' : 'Supprimer'}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default DnsRecordCard; 