import axios from 'axios';

/**
 * API URL from environment or default
 */
const API_URL = process.env.REACT_APP_API_URL || '/api/v1';

/**
 * Get all DNS records
 * 
 * @returns {Promise} - DNS records list response
 */
export const getDnsRecords = async () => {
  try {
    const response = await axios.get(`${API_URL}/dns/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching DNS records:', error);
    throw error;
  }
};

/**
 * Get Cloudflare zones for the current user
 * 
 * @returns {Promise} - List of Cloudflare zones
 */
export const getCloudflareZones = async () => {
  try {
    const response = await axios.get(`${API_URL}/dns/zones`);
    return response.data.zones;
  } catch (error) {
    console.error('Error fetching Cloudflare zones:', error);
    throw error;
  }
};

/**
 * Get current public IP address
 * 
 * @returns {Promise} - Current IP address
 */
export const getCurrentIp = async () => {
  try {
    const response = await axios.get(`${API_URL}/dns/current-ip`);
    return response.data.ip;
  } catch (error) {
    console.error('Error fetching current IP:', error);
    throw error;
  }
};

/**
 * Get a specific DNS record by ID
 * 
 * @param {number} id - DNS record ID
 * @returns {Promise} - DNS record response
 */
export const getDnsRecord = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/dns/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching DNS record ${id}:`, error);
    throw error;
  }
};

/**
 * Create a new DNS record
 * 
 * @param {Object} record - DNS record data
 * @returns {Promise} - Created DNS record response
 */
export const createDnsRecord = async (record) => {
  try {
    const response = await axios.post(`${API_URL}/dns/`, record);
    return response.data;
  } catch (error) {
    console.error('Error creating DNS record:', error);
    throw error;
  }
};

/**
 * Update an existing DNS record
 * 
 * @param {number} id - DNS record ID
 * @param {Object} record - Updated DNS record data
 * @returns {Promise} - Updated DNS record response
 */
export const updateDnsRecord = async (id, record) => {
  try {
    const response = await axios.put(`${API_URL}/dns/${id}`, record);
    return response.data;
  } catch (error) {
    console.error(`Error updating DNS record ${id}:`, error);
    throw error;
  }
};

/**
 * Delete a DNS record
 * 
 * @param {number} id - DNS record ID
 * @returns {Promise} - Delete response
 */
export const deleteDnsRecord = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/dns/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting DNS record ${id}:`, error);
    throw error;
  }
};

/**
 * Update the IP address for a DNS record
 * 
 * @param {number} id - DNS record ID
 * @returns {Promise} - Updated DNS record response
 */
export const updateDnsRecordIp = async (id) => {
  try {
    const response = await axios.post(`${API_URL}/dns/${id}/update-ip`);
    return response.data;
  } catch (error) {
    console.error(`Error updating IP for DNS record ${id}:`, error);
    throw error;
  }
};

/**
 * Get all Cloudflare DNS records for a zone
 * 
 * @param {string} zoneId - Cloudflare zone ID
 * @returns {Promise} - Cloudflare DNS records response
 */
export const getCloudflareDnsRecords = async (zoneId) => {
  try {
    const response = await axios.get(`${API_URL}/dns/records/${zoneId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching Cloudflare DNS records for zone ${zoneId}:`, error);
    throw error;
  }
};

/**
 * Update IP address for all DNS records
 * 
 * @returns {Promise} - Response with updated records count
 */
export const updateAllDnsRecordIps = async () => {
  try {
    const response = await axios.post(`${API_URL}/dns/update-all-ips`);
    return response.data;
  } catch (error) {
    console.error('Error updating all DNS records IPs:', error);
    throw error;
  }
};
