// Configuração da API
export const API_CONFIG = {
  // URL da API Gateway (Lambda)
  BASE_URL: 'https://n3f0p33lf4.execute-api.us-east-1.amazonaws.com/prod',
  
  // Endpoints
  ENDPOINTS: {
    // Admin
    ADMIN_REGRESSIVOS: '/api/admin/regressivos',
    ADMIN_SQUADS_CONFIG: '/api/admin/squads-config',
    
    // Quality
    QUALITY_REGRESSIVOS: '/api/quality/regressivos',
    QUALITY_SQUAD_MODULO: '/api/quality/squad-modulo',
    
    // Health
    HEALTH: '/health'
  }
}

// Headers padrão
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

// Função helper para fazer requests
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`
  
  const config = {
    headers: DEFAULT_HEADERS,
    ...options
  }
  
  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('API Request Error:', error)
    throw error
  }
}

