export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface Game {
  id: string
  title: string
  team_name: string
}

export interface AIChatContextType {
  messages: ChatMessage[]
  isOpen: boolean
  isLoading: boolean
  inputValue: string
  sendMessage: (message: string) => Promise<void>
  toggleChat: () => void
  clearMessages: () => void
  setInputValue: (value: string) => void
}