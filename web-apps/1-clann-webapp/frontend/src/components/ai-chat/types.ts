export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface Game {
  id: string
  title: string
  team_name: string
  is_demo?: boolean
}

export type CoachPersonality = 'ferguson' | 'mourinho' | 'wenger'

export interface Coach {
  id: CoachPersonality
  name: string
  title: string
  image: string
  personality: string
  systemPrompt: string
}

export interface AIChatContextType {
  messages: ChatMessage[]
  isOpen: boolean
  isLoading: boolean
  inputValue: string
  selectedCoach: Coach | null
  sendMessage: (message: string) => Promise<void>
  toggleChat: () => void
  clearMessages: () => void
  setInputValue: (value: string) => void
  setSelectedCoach: (coach: Coach) => void
  game: Game
}