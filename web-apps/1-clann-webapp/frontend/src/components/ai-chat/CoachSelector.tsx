'use client'

import { useState } from 'react'
import { Coach } from './types'
import { COACHES } from './coaches'

interface CoachSelectorProps {
  selectedCoach: Coach | null
  onCoachSelect: (coach: Coach) => void
  onClose: () => void
}

export default function CoachSelector({ selectedCoach, onCoachSelect, onClose }: CoachSelectorProps) {
  const [isOpen, setIsOpen] = useState(true)

  const handleCoachSelect = (coach: Coach) => {
    onCoachSelect(coach)
    setIsOpen(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl border border-gray-700 p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white mb-2">Choose Your AI Coach</h2>
          <p className="text-gray-400">Select a legendary manager to guide your tactical discussions</p>
        </div>

        <div className="grid gap-4">
          {COACHES.map((coach) => (
            <button
              key={coach.id}
              onClick={() => handleCoachSelect(coach)}
              className="group relative bg-gray-800 hover:bg-gray-700 rounded-xl p-6 border border-gray-600 hover:border-green-500 transition-all duration-200 text-left"
            >
              <div className="flex items-start space-x-4">
                {/* Coach Image */}
                <div className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 border-2 border-gray-600">
                  <img 
                    src={coach.image} 
                    alt={coach.name}
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-xl font-bold text-white">{coach.name}</h3>
                    <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">
                      {coach.title}
                    </span>
                  </div>
                  
                  <p className="text-gray-300 text-sm leading-relaxed">
                    {coach.personality}
                  </p>
                </div>

                {/* Selection indicator */}
                {selectedCoach?.id === coach.id && (
                  <div className="absolute top-3 right-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="mt-6 flex justify-between items-center">
          <p className="text-xs text-gray-500">
            Choose a coaching style that matches your team's philosophy
          </p>
          <button
            onClick={() => {
              setIsOpen(false)
              onClose()
            }}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}