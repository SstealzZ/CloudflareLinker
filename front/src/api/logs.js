import axios from 'axios';

/**
 * API URL from environment or default
 */
const API_URL = process.env.REACT_APP_API_URL || '/api/v1';

/**
 * Get user logs
 * 
 * @param {number} skip - Number of logs to skip
 * @param {number} limit - Maximum number of logs to return
 * @returns {Promise} - Logs list response
 */
export const getUserLogs = async (skip = 0, limit = 100) => {
  try {
    const response = await axios.get(`${API_URL}/logs/?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user logs:', error);
    throw error;
  }
};

/**
 * Get system logs
 * 
 * @param {number} skip - Number of logs to skip
 * @param {number} limit - Maximum number of logs to return
 * @returns {Promise} - System logs list response
 */
export const getSystemLogs = async (skip = 0, limit = 100) => {
  try {
    const response = await axios.get(`${API_URL}/logs/system?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching system logs:', error);
    throw error;
  }
}; 