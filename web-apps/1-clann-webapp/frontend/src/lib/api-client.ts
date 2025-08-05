import { VMFileMap, EnhancedAnalysis } from '@/types/analysis'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3002'

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

  async getDemoGames() {
    return this.request<{ games: any[] }>('/api/games/demo')
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

  async leaveTeam(teamId: string) {
    return this.request<{ message: string; success: boolean }>(`/api/teams/${teamId}/leave`, {
      method: 'POST'
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
      // Extract S3 key from full S3 URL if provided
      let s3Key = data.videoUrl
      if (data.videoUrl.startsWith('s3://')) {
        s3Key = data.videoUrl.replace('s3://clannai-video-storage/', '')
      } else if (data.videoUrl.includes('amazonaws.com')) {
        // Handle HTTPS S3 URLs
        const urlParts = data.videoUrl.split('clannai-video-storage/')
        s3Key = urlParts[1] || data.videoUrl
      }
      
      await this.request(`/api/games/${gameId}/upload-video`, {
        method: 'POST',
        body: JSON.stringify({ s3Key })
      })
    }
    
    if (data.events) {
      await this.request(`/api/games/${gameId}/analysis`, {
        method: 'POST',
        body: JSON.stringify({ analysis: data.events })
      })
    }
    
    if (data.status) {
      await this.request(`/api/games/${gameId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: data.status })
      })
    }
  }

  // Get single game for viewing
  async getGame(gameId: string) {
    return this.request(`/api/games/${gameId}`);
  }

  // Join team by invite code
  async joinTeamByCode(inviteCode: string) {
    return this.request<{ team: any }>('/api/teams/join-by-code', {
      method: 'POST',
      body: JSON.stringify({ inviteCode })
    })
  }

  // AI Chat
  async chatWithAI(gameId: string, message: string, chatHistory: any[] = []) {
    return this.request<{
      response: string
      gameStats: any
      timestamp: string
    }>(`/api/ai-chat/game/${gameId}`, {
      method: 'POST',
      body: JSON.stringify({ message, chatHistory })
    })
  }

  // VM Analysis Processing
  async processVMAnalysis(gameId: string, vmFiles: VMFileMap) {
    return this.request<{
      message: string
      filesProcessed: number
      game: any
    }>(`/api/games/${gameId}/vm-analysis`, {
      method: 'POST',
      body: JSON.stringify({ vmFiles })
    })
  }

  // Parse VM file list format into file map
  parseVMFileList(fileList: string): VMFileMap {
    const files: VMFileMap = {}
    const lines = fileList.split('\n').filter(line => line.includes('='))
    
    lines.forEach(line => {
      const [filename, url] = line.split('=')
      if (filename && url) {
        files[filename.trim()] = url.trim()
      }
    })
    
    return files
  }

  // Enhanced analysis file management
  async updateAnalysisFiles(gameId: string, s3AnalysisFiles: Record<string, string>) {
    return this.request(`/api/games/${gameId}/analysis-files`, {
      method: 'POST',
      body: JSON.stringify({ s3AnalysisFiles })
    })
  }

  // Fetch and preview S3 content for validation
  async previewS3Content(s3Url: string, maxLength: number = 1000) {
    try {
      const response = await fetch(s3Url)
      if (!response.ok) throw new Error(`Failed to fetch: ${response.status}`)
      
      const contentType = response.headers.get('content-type') || ''
      
      if (contentType.includes('application/json')) {
        const json = await response.json()
        return {
          type: 'json',
          preview: JSON.stringify(json, null, 2).substring(0, maxLength),
          size: JSON.stringify(json).length
        }
      } else {
        const text = await response.text()
        return {
          type: 'text',
          preview: text.substring(0, maxLength),
          size: text.length
        }
      }
    } catch (error) {
      return {
        type: 'error',
        preview: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        size: 0
      }
    }
  }
}

export const apiClient = new ApiClient()
export default apiClient 