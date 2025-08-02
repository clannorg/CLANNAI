'use client'

import React from 'react'
import { useAIChat } from './AIChatProvider'

const ChatInput: React.FC = () => {
  const { 
    inputValue, 
    setInputValue, 
    sendMessage, 
    isLoading, 
    messages,
    clearMessages 
  } = useAIChat()

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return
    await sendMessage(inputValue)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="border-t border-white/20 p-4 bg-black/50 backdrop-blur-sm">
      <div className="flex items-end space-x-3">
        <input
          type="text"
          placeholder="Ask the AI coach..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white text-sm placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400/50 backdrop-blur-sm transition-all duration-200 disabled:opacity-50"
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          className="flex items-center justify-center w-12 h-12 bg-blue-500 hover:bg-blue-600 disabled:bg-white/10 disabled:text-white/40 text-white rounded-xl font-medium disabled:cursor-not-allowed transition-all duration-200 border border-blue-400 disabled:border-white/10 shadow-lg"
          title="Send Message"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
      
      {messages.length > 0 && (
        <button
          onClick={clearMessages}
          className="flex items-center space-x-1 text-xs text-white/60 hover:text-white/80 mt-3 px-2 py-1 rounded-lg hover:bg-white/5 transition-all duration-200"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Clear chat</span>
        </button>
      )}
    </div>
  )
}

export default ChatInput