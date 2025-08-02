// Enhanced Analysis Types for ClannAI Video Player
// Supports comprehensive VM analysis output

export interface GameEvent {
  type: string
  timestamp: number
  player?: string
  description?: string
  team?: string
}

export interface PlayerStats {
  name?: string
  position?: string
  distanceCovered?: number
  sprints?: number
  goals?: number
  shots?: number
  passAccuracy?: number
  touches?: number
  heatmapUrl?: string
}

export interface TeamStats {
  possession?: number
  passes?: number
  passAccuracy?: number
  shots?: number
  shotsOnTarget?: number
  corners?: number
  fouls?: number
  formation?: string[]
}

export interface TacticalAnalysis {
  red?: string
  yellow?: string
  black?: string
  summary?: string
}

export interface Timeline {
  complete?: string
  validated?: string
  accuracy?: string
}

export interface AnalysisMetadata {
  processedFiles?: string[]
  processedAt?: string
  groundTruth?: any
  sourceFiles?: Record<string, string>
  vmId?: string
}

export interface AnalysisAssets {
  heatmaps?: Record<string, string>
  activityCharts?: Record<string, string>
  sprintDiagrams?: Record<string, string>
  positionMaps?: Record<string, string>
}

// Main enhanced analysis structure
export interface EnhancedAnalysis {
  events: GameEvent[]
  playerStats?: Record<string, Record<string, PlayerStats>>
  teamStats?: Record<string, TeamStats>
  tacticalAnalysis?: TacticalAnalysis
  timeline?: Timeline
  metadata?: AnalysisMetadata
  assets?: AnalysisAssets
}

// VM File processing types
export interface VMFileMap {
  [filename: string]: string // filename -> S3 URL
}

export interface VMProcessingResult {
  success: boolean
  filesProcessed: number
  errors?: string[]
  analysis: EnhancedAnalysis
}

// Game interface enhanced with new analysis
export interface Game {
  id: string
  title: string
  description: string
  video_url?: string
  s3_key?: string
  s3Url?: string
  status: string
  ai_analysis?: EnhancedAnalysis | GameEvent[] // Support both legacy and new format
  team_id: string
  team_name: string
  team_color: string
  created_at: string
  has_analysis?: boolean
  uploaded_by_name?: string
  uploaded_by_email?: string
}

// Video player state types
export interface VideoPlayerState {
  currentTime: number
  duration: number
  isPlaying: boolean
  isMuted: boolean
  currentEventIndex: number
  showEvents: boolean
  showAnalysis: boolean
  activeAnalysisTab: 'events' | 'tactical' | 'timeline' | 'stats' | 'assets'
}

export interface EventFilters {
  eventTypes: Record<string, boolean>
  teams: string // 'both' | 'red' | 'black' | 'yellow'
  timeRange: [number, number]
  searchText: string
}

export interface TeamScores {
  red: number
  black: number
  yellow?: number
}