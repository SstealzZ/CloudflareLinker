import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges class names with TailwindCSS classes
 * 
 * @param {Array} inputs - Class names to merge
 * @returns {string} - Merged class names
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format a date string to a human-readable format
 * 
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string or placeholder if date is invalid
 */
export function formatDate(dateString) {
  if (!dateString) {
    return 'N/A';
  }
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Date invalide';
    }
    
    return new Intl.DateTimeFormat('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch (error) {
    return 'Date invalide';
  }
}

/**
 * Truncate a string to a specified length
 * 
 * @param {string} str - String to truncate
 * @param {number} length - Maximum length
 * @returns {string} - Truncated string
 */
export function truncate(str, length) {
  if (!str) return '';
  return str.length > length ? `${str.substring(0, length)}...` : str;
} 