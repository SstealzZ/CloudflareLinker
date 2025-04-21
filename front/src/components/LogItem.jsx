import React from 'react';
import { formatDate } from '../lib/utils';

/**
 * Component to display a log item
 * 
 * @param {Object} props - Component props
 * @param {Object} props.log - Log data
 * @returns {JSX.Element} - Log item component
 */
const LogItem = ({ log }) => {
  /**
   * Get background color based on log level
   */
  const getLevelColor = () => {
    switch (log.level) {
      case 'INFO':
        return 'bg-blue-50 dark:bg-blue-900/20';
      case 'WARNING':
        return 'bg-yellow-50 dark:bg-yellow-900/20';
      case 'ERROR':
        return 'bg-red-50 dark:bg-red-900/20';
      case 'SUCCESS':
        return 'bg-green-50 dark:bg-green-900/20';
      default:
        return 'bg-gray-50 dark:bg-gray-900/20';
    }
  };

  /**
   * Get text color based on log level
   */
  const getLevelTextColor = () => {
    switch (log.level) {
      case 'INFO':
        return 'text-blue-600 dark:text-blue-300';
      case 'WARNING':
        return 'text-yellow-600 dark:text-yellow-300';
      case 'ERROR':
        return 'text-red-600 dark:text-red-300';
      case 'SUCCESS':
        return 'text-green-600 dark:text-green-300';
      default:
        return 'text-gray-600 dark:text-gray-300';
    }
  };

  /**
   * Format the log message to highlight DNS record names
   */
  const formatMessage = () => {
    // If the message contains a DNS record name, highlight it
    if (log.message.includes(' for ') && !log.message.includes('update completed')) {
      const parts = log.message.split(' for ');
      const action = parts[0];
      const remainingText = parts[1];
      
      // Check if there's a DNS record name in parentheses or after a colon
      if (remainingText.includes('(') || remainingText.includes(':')) {
        const recordName = remainingText.split(/[\(:]/)[0].trim();
        const rest = remainingText.substring(recordName.length);
        
        return (
          <>
            <span>{action} for </span>
            <span className="font-semibold">{recordName}</span>
            <span>{rest}</span>
          </>
        );
      }
    }
    
    return log.message;
  };

  return (
    <div className={`p-3 rounded-md mb-2 ${getLevelColor()}`}>
      <div className="flex justify-between items-start">
        <div className="flex items-start gap-2">
          <span className={`font-medium px-2 py-0.5 rounded ${getLevelTextColor()} bg-opacity-20`}>
            {log.level}
          </span>
          <span className="text-sm">{formatMessage()}</span>
        </div>
        <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
          {formatDate(log.created_at)}
        </span>
      </div>
      
      {log.details && (
        <div className="mt-2 text-sm text-muted-foreground pl-14">
          {log.details}
        </div>
      )}
      
      {log.ip_address && (
        <div className="mt-1 text-xs text-muted-foreground pl-14 font-mono">
          IP: {log.ip_address}
        </div>
      )}
    </div>
  );
};

export default LogItem; 