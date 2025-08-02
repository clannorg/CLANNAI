'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
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

  // Listen for insight card clicks and check for dashboard context
  useEffect(() => {
    // Check for context from dashboard on component mount
    const dashboardContext = sessionStorage.getItem('aiCoachContext')
    if (dashboardContext) {
      try {
        const { type, details, gameTitle } = JSON.parse(dashboardContext)
        
        // Clear the stored context
        sessionStorage.removeItem('aiCoachContext')
        
        // Open the chat and send contextual message
        setIsOpen(true)
        
        const contextMessage = `I came from the dashboard to discuss the ${type} for ${gameTitle}. ${details ? `Specifically: ${details}` : ''}`
        
        setTimeout(() => {
          sendMessage(contextMessage)
        }, 1000) // Give more time for page to load
      } catch (error) {
        console.error('Error parsing dashboard context:', error)
      }
    }

    const handleAICoachContext = async (event: Event) => {
      const customEvent = event as CustomEvent
      const { context, details } = customEvent.detail
      
      // Open the chat
      setIsOpen(true)
      
      // Send a contextual message to the AI
      const contextMessage = `I'd like to discuss the ${context}. ${details ? `Specifically: ${details}` : ''}`
      
      // Wait a moment for the chat to open, then send the message
      setTimeout(() => {
        sendMessage(contextMessage)
      }, 500)
    }

    window.addEventListener('openAICoachWithContext', handleAICoachContext)
    
    return () => {
      window.removeEventListener('openAICoachWithContext', handleAICoachContext)
    }
  }, [sendMessage])

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