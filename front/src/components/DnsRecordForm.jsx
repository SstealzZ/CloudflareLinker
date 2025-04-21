import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Button from './ui/button';
import Input from './ui/input';
import { getCloudflareZones, getCurrentIp } from '../api/dns';

/**
 * Form component for creating or editing DNS records
 * 
 * @param {Object} props - Component props
 * @param {Function} props.onSubmit - Callback when form is submitted
 * @param {Function} props.onCancel - Callback when form is canceled
 * @param {Object} [props.initialData] - Initial data for editing
 * @returns {JSX.Element} - DNS record form component
 */
const DnsRecordForm = ({ onSubmit, onCancel, initialData = null }) => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    zone_id: initialData?.zone_id || '',
    zone_name: initialData?.zone_name || '',
    record_type: initialData?.record_type || 'A',
    record_name: initialData?.record_name || '',
    content: initialData?.content || '',
    ttl: initialData?.ttl || 1, // Auto
    proxied: initialData?.proxied || false,
    auto_update: initialData?.auto_update || true
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState({
    zones: true,
    ip: false
  });
  const [zones, setZones] = useState([]);
  const [currentIp, setCurrentIp] = useState('');

  /**
   * Load Cloudflare zones and current IP
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(prev => ({ ...prev, zones: true }));
        const zonesData = await getCloudflareZones();
        setZones(zonesData);
        
        if (zonesData.length > 0 && !initialData) {
          setFormData(prev => ({
            ...prev,
            zone_id: zonesData[0].id,
            zone_name: zonesData[0].name
          }));
        }
      } catch (error) {
        console.error('Error loading zones:', error);
        setError('Erreur lors du chargement des zones Cloudflare');
      } finally {
        setLoading(prev => ({ ...prev, zones: false }));
      }
    };
    
    loadData();
  }, [initialData]);

  /**
   * Load current IP when needed
   */
  useEffect(() => {
    // Load current IP if A/AAAA record is selected and auto_update is enabled
    if ((formData.record_type === 'A' || formData.record_type === 'AAAA') && formData.auto_update) {
      const fetchIp = async () => {
        try {
          setLoading(prev => ({ ...prev, ip: true }));
          const ip = await getCurrentIp();
          setCurrentIp(ip);
          
          // Only set content if it's empty or user hasn't manually changed it
          if (!formData.content || formData.content === currentIp) {
            setFormData(prev => ({ ...prev, content: ip }));
          }
        } catch (error) {
          console.error('Error fetching IP:', error);
        } finally {
          setLoading(prev => ({ ...prev, ip: false }));
        }
      };
      
      fetchIp();
    }
  }, [formData.record_type, formData.auto_update]);

  /**
   * Handle select zone change
   * 
   * @param {Event} e - Select change event
   */
  const handleZoneChange = (e) => {
    const zoneId = e.target.value;
    const selectedZone = zones.find(zone => zone.id === zoneId);
    
    if (selectedZone) {
      setFormData(prev => ({
        ...prev,
        zone_id: zoneId,
        zone_name: selectedZone.name
      }));
    }
  };

  /**
   * Handle input changes
   * 
   * @param {Event} e - Input change event
   */
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  /**
   * Handle form submission
   * 
   * @param {Event} e - Form submit event
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.zone_id || !formData.zone_name || !formData.record_name) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    if ((formData.record_type === 'A' || formData.record_type === 'AAAA') && !formData.content && !formData.auto_update) {
      setError('Le contenu est obligatoire pour les enregistrements A et AAAA si la mise à jour automatique est désactivée');
      return;
    }
    
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-500/10 text-red-500 p-3 rounded-md text-sm mb-4">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading.zones ? (
          <div className="col-span-2 text-center p-4">
            <div className="animate-pulse text-muted-foreground">Chargement des zones Cloudflare...</div>
          </div>
        ) : zones.length > 0 ? (
          <div className="space-y-2 col-span-2">
            <label htmlFor="zone_id" className="text-sm font-medium">
              Zone Cloudflare *
            </label>
            <select
              id="zone_id"
              name="zone_id"
              value={formData.zone_id}
              onChange={handleZoneChange}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
              required
            >
              {zones.map(zone => (
                <option key={zone.id} value={zone.id}>
                  {zone.name} ({zone.status})
                </option>
              ))}
            </select>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              <label htmlFor="zone_id" className="text-sm font-medium">
                ID de Zone Cloudflare *
              </label>
              <Input
                id="zone_id"
                name="zone_id"
                value={formData.zone_id}
                onChange={handleChange}
                placeholder="ex: 123e4567-e89b-12d3-a456-426614174000"
                required
              />
              <p className="text-xs text-muted-foreground">
                Identifiant unique de votre zone Cloudflare
              </p>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="zone_name" className="text-sm font-medium">
                Nom de Zone *
              </label>
              <Input
                id="zone_name"
                name="zone_name"
                value={formData.zone_name}
                onChange={handleChange}
                placeholder="ex: example.com"
                required
              />
              <p className="text-xs text-muted-foreground">
                Nom de domaine de votre zone
              </p>
            </div>
          </>
        )}
        
        <div className="space-y-2">
          <label htmlFor="record_type" className="text-sm font-medium">
            Type d'enregistrement *
          </label>
          <select
            id="record_type"
            name="record_type"
            value={formData.record_type}
            onChange={handleChange}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
            required
          >
            <option value="A">A (IPv4)</option>
            <option value="AAAA">AAAA (IPv6)</option>
            <option value="CNAME">CNAME</option>
            <option value="TXT">TXT</option>
            <option value="MX">MX</option>
          </select>
        </div>
        
        <div className="space-y-2">
          <label htmlFor="record_name" className="text-sm font-medium">
            Nom d'enregistrement *
          </label>
          <Input
            id="record_name"
            name="record_name"
            value={formData.record_name}
            onChange={handleChange}
            placeholder="ex: www"
            required
          />
          <p className="text-xs text-muted-foreground">
            Sous-domaine ou @ pour l'apex
          </p>
        </div>
        
        <div className="space-y-2">
          <label htmlFor="content" className="text-sm font-medium">
            Contenu {!formData.auto_update || (formData.record_type !== 'A' && formData.record_type !== 'AAAA') ? '*' : ''}
          </label>
          <Input
            id="content"
            name="content"
            value={formData.content}
            onChange={handleChange}
            placeholder={formData.record_type === 'A' ? "ex: 192.168.1.1" : "ex: example.com"}
            disabled={formData.auto_update && (formData.record_type === 'A' || formData.record_type === 'AAAA')}
            required={!formData.auto_update || (formData.record_type !== 'A' && formData.record_type !== 'AAAA')}
          />
          {formData.auto_update && (formData.record_type === 'A' || formData.record_type === 'AAAA') ? (
            <p className="text-xs text-muted-foreground">
              IP détectée automatiquement: {currentIp || 'chargement...'}
            </p>
          ) : (
            <p className="text-xs text-muted-foreground">
              {formData.record_type === 'A' || formData.record_type === 'AAAA' 
                ? "Adresse IP cible"
                : "Valeur de l'enregistrement"}
            </p>
          )}
        </div>
        
        <div className="space-y-2">
          <label htmlFor="ttl" className="text-sm font-medium">
            TTL
          </label>
          <select
            id="ttl"
            name="ttl"
            value={formData.ttl}
            onChange={handleChange}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
          >
            <option value="1">Auto</option>
            <option value="60">1 minute</option>
            <option value="300">5 minutes</option>
            <option value="1800">30 minutes</option>
            <option value="3600">1 heure</option>
            <option value="86400">1 jour</option>
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="proxied"
            name="proxied"
            checked={formData.proxied}
            onChange={handleChange}
            className="rounded border-input"
          />
          <label htmlFor="proxied" className="text-sm font-medium">
            Proxied (Protection Cloudflare)
          </label>
        </div>
        
        {(formData.record_type === 'A' || formData.record_type === 'AAAA') && (
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="auto_update"
              name="auto_update"
              checked={formData.auto_update}
              onChange={handleChange}
              className="rounded border-input"
            />
            <label htmlFor="auto_update" className="text-sm font-medium">
              Mise à jour automatique de l'IP
            </label>
          </div>
        )}
      </div>
      
      <div className="flex justify-end space-x-2">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
        >
          Annuler
        </Button>
        <Button type="submit">
          {initialData ? 'Mettre à jour' : 'Créer'}
        </Button>
      </div>
    </form>
  );
};

export default DnsRecordForm; 