'use client'

import React, { createContext, useContext, useState } from 'react'
import apiClient from '@/lib/api-client'
import { ChatMessage, Game, AIChatContextType } from './types'

const AIChatContext = createContext<AIChatContextType | undefined>(undefined)

interface AIChatProviderProps {
  children: React.ReactNode
  game: Game
}

export const AIChatProvider: React.FC<AIChatProviderProps> = ({ children, game }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [inputValue, setInputValue] = useState('')

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading || !game) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await apiClient.chatWithAI(
        game.id,
        userMessage.content,
        messages.map(msg => ({ role: msg.role, content: msg.content }))
      )

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: '⚠️ Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const toggleChat = () => setIsOpen(prev => !prev)
  const clearMessages = () => setMessages([])

  const contextValue: AIChatContextType = {
    messages,
    isOpen,
    isLoading,
    inputValue,
    sendMessage,
    toggleChat,
    clearMessages,
    setInputValue
  }

  return (
    <AIChatContext.Provider value={contextValue}>
      {children}
    </AIChatContext.Provider>
  )
}

export const useAIChat = () => {
  const context = useContext(AIChatContext)
  if (context === undefined) {
    throw new Error('useAIChat must be used within an AIChatProvider')
  }
  return context
}