import axios from 'axios';

/**
 * API URL from environment or default
 */
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Check if the application requires first-time setup
 * 
 * @returns {Promise<boolean>} - Whether setup is needed
 */
export const checkSetupStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/auth/setup-status`);
    return response.data.needs_setup;
  } catch (error) {
    console.error('Error checking setup status:', error);
    return false;
  }
};

/**
 * Perform first-time setup
 * 
 * @param {Object} setupData - Setup data with admin user information
 * @returns {Promise<Object>} - Setup result with token
 */
export const performSetup = async (setupData) => {
  try {
    const response = await axios.post(`${API_URL}/auth/setup`, setupData);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || 'Une erreur est survenue lors de la configuration'
    };
  }
}; 