// API Configuration for connecting to your VPS backend
// Set VITE_API_URL in your environment or .env file

export const API_CONFIG = {
  // The base URL of your backend API
  // In development: http://localhost:8000
  // In production: https://api.yourdomain.com or https://yourdomain.com
  baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // API version prefix
  apiVersion: '/api/v1',
  
  // Full API URL
  get apiUrl() {
    return `${this.baseUrl}${this.apiVersion}`;
  },
  
  // Timeout settings (ms)
  timeout: 30000,
  
  // Retry settings
  maxRetries: 3,
  retryDelay: 1000,
};

// Check if we're connected to the backend
export async function checkBackendConnection(): Promise<{
  connected: boolean;
  message: string;
  version?: string;
}> {
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    
    if (response.ok) {
      const data = await response.json().catch(() => ({}));
      return {
        connected: true,
        message: 'Connected to backend',
        version: data.version,
      };
    }
    
    return {
      connected: false,
      message: `Backend returned status ${response.status}`,
    };
  } catch (error) {
    return {
      connected: false,
      message: error instanceof Error ? error.message : 'Failed to connect to backend',
    };
  }
}

// Export for use in components
export default API_CONFIG;
