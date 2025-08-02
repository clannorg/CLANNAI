'use client'

import React from 'react'
import { useAIChat } from './AIChatProvider'

interface ChatToggleButtonProps {
  variant?: 'primary' | 'floating'
  className?: string
}

const ChatToggleButton: React.FC<ChatToggleButtonProps> = ({ 
  variant = 'primary',
  className = '' 
}) => {
  const { isOpen, toggleChat } = useAIChat()

  if (variant === 'floating') {
    return (
      <button
        onClick={toggleChat}
        className={`block bg-black/80 backdrop-blur-sm rounded-lg p-3 text-white hover:text-gray-300 transition-colors ${className}`}
        title="Show AI Chat"
      >
        🤖 AI Coach
      </button>
    )
  }

  return (
    <button
      onClick={toggleChat}
      className={`group flex items-center space-x-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 border shadow-lg ${
        isOpen 
          ? 'bg-blue-500/20 hover:bg-blue-500/30 border-blue-400/40 text-blue-200' 
          : 'bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white'
      } ${className}`}
      title="Toggle AI Chat"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
      <span style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>AI Coach</span>
    </button>
  )
}

export default ChatToggleButton