'use client'

import React from 'react'
import { useAIChat } from './AIChatProvider'

const AIChatSidebar: React.FC = () => {
  const { isOpen, toggleChat, messages, isLoading, inputValue, setInputValue, sendMessage, clearMessages } = useAIChat()

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

  if (!isOpen) return null

  return (
    <div className="absolute top-0 left-0 h-full w-full md:w-80 bg-black/90 backdrop-blur-sm border-r border-gray-700 flex flex-col z-30">
      <div className="sticky top-0 bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-white font-semibold">AI Coach</h3>
          </div>
          <button
            onClick={toggleChat}
            className="flex items-center justify-center w-8 h-8 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 border border-white/10 hover:border-white/20"
            title="Hide Chat"
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-400">
          Ask questions about tactics, player performance, or get coaching advice.
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h4 className="text-white font-medium mb-2">Welcome to AI Coach!</h4>
            <p className="text-gray-400 text-sm">Try asking about game analysis</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${
                message.role === 'user' 
                  ? 'bg-blue-500 text-white ml-4' 
                  : 'bg-white/10 text-gray-100 mr-4'
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
              </div>
            </div>
          ))
        )}
      </div>
      
      <div className="border-t border-white/20 p-4">
        <div className="flex items-end space-x-3">
          <input
            type="text"
            placeholder="Ask the AI coach..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white text-sm placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="flex items-center justify-center w-12 h-12 bg-blue-500 hover:bg-blue-600 disabled:bg-white/10 text-white rounded-xl transition-all duration-200"
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
            className="text-xs text-white/60 hover:text-white/80 mt-3 px-2 py-1 rounded-lg hover:bg-white/5"
          >
            Clear chat
          </button>
        )}
      </div>
    </div>
  )
}

export default AIChatSidebar