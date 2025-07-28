const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

class ApiClient {
  private getAuthHeaders() {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Auth methods
  async login(email: string, password: string) {
    return this.request<{ token: string; user: any }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })
  }

  async register(email: string, password: string, phone: string) {
    return this.request<{ token: string; user: any }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, phone })
    })
  }

  async getCurrentUser() {
    return this.request<{ user: any }>('/api/auth/me')
  }

  // Games methods
  async getUserGames() {
    return this.request<{ games: any[] }>('/api/games')
  }

  async createGame(gameData: {
    title: string
    description?: string
    videoUrl: string
    teamId: string
  }) {
    return this.request<{ game: any }>('/api/games', {
      method: 'POST',
      body: JSON.stringify(gameData)
    })
  }

  // Teams methods
  async getUserTeams() {
    return this.request<{ teams: any[] }>('/api/teams/my-teams')
  }

  async joinTeam(teamCode: string) {
    return this.request<{ team: any }>('/api/teams/join', {
      method: 'POST',
      body: JSON.stringify({ teamCode })
    })
  }

  async createTeam(teamData: {
    name: string
    description?: string
    color?: string
  }) {
    return this.request<{ team: any }>('/api/teams/create', {
      method: 'POST',
      body: JSON.stringify(teamData)
    })
  }

  async getDemoTeamCodes() {
    return this.request<{ codes: any[] }>('/api/teams/codes/demo')
  }

  // Health check
  async healthCheck() {
    return this.request<{ status: string }>('/health')
  }

  // Company methods
  async getCompanyGames(status?: string) {
    const params = status ? `?status=${status}` : ''
    return this.request<{ games: any[], pagination: any }>(`/api/company/games${params}`)
  }

  async getCompanyStats() {
    return this.request<{ stats: any }>('/api/company/stats')
  }

  async getPendingVeoGames() {
    return this.request<{ games: any[] }>('/api/company/pending-veo')
  }

  async updateGameAnalysis(gameId: string, data: {
    videoUrl?: string
    events?: any
    status?: string
  }) {
    if (data.videoUrl) {
      await this.request(`/api/games/${gameId}/upload-video`, {
        method: 'POST',
        body: JSON.stringify({ videoUrl: data.videoUrl })
      })
    }
    
    if (data.events) {
      await this.request(`/api/games/${gameId}/analysis`, {
        method: 'POST',
        body: JSON.stringify(data.events)
      })
    }
    
    if (data.status) {
      await this.request(`/api/games/${gameId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: data.status })
      })
    }
  }
}

export const apiClient = new ApiClient()
export default apiClient 