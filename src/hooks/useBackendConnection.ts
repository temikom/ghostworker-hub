import { useState, useEffect, useCallback } from 'react';
import { checkBackendConnection, API_CONFIG } from '@/config/api';

interface BackendStatus {
  isConnected: boolean;
  isChecking: boolean;
  message: string;
  version?: string;
  lastChecked?: Date;
}

export function useBackendConnection() {
  const [status, setStatus] = useState<BackendStatus>({
    isConnected: false,
    isChecking: true,
    message: 'Checking connection...',
  });

  const checkConnection = useCallback(async () => {
    setStatus(prev => ({ ...prev, isChecking: true }));
    
    const result = await checkBackendConnection();
    
    setStatus({
      isConnected: result.connected,
      isChecking: false,
      message: result.message,
      version: result.version,
      lastChecked: new Date(),
    });
    
    return result.connected;
  }, []);

  useEffect(() => {
    checkConnection();
    
    // Optionally re-check periodically
    const interval = setInterval(checkConnection, 60000); // Every minute
    
    return () => clearInterval(interval);
  }, [checkConnection]);

  return {
    ...status,
    apiUrl: API_CONFIG.apiUrl,
    baseUrl: API_CONFIG.baseUrl,
    checkConnection,
  };
}

export default useBackendConnection;
