'use client'

import { useState, useEffect } from 'react'

interface OrientationState {
  isPortrait: boolean
  isLandscape: boolean
  orientation: 'portrait' | 'landscape'
}

export function useOrientation(): OrientationState {
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('landscape')

  useEffect(() => {
    // Function to update orientation based on window dimensions
    const updateOrientation = () => {
      if (typeof window !== 'undefined') {
        const isPortraitMode = window.innerHeight > window.innerWidth
        setOrientation(isPortraitMode ? 'portrait' : 'landscape')
      }
    }

    // Set initial orientation
    updateOrientation()

    // Listen for resize events (includes orientation changes)
    window.addEventListener('resize', updateOrientation)
    
    // Listen for orientation change events (mobile-specific)
    window.addEventListener('orientationchange', () => {
      // Small delay to ensure dimensions are updated after orientation change
      setTimeout(updateOrientation, 100)
    })

    // Cleanup listeners
    return () => {
      window.removeEventListener('resize', updateOrientation)
      window.removeEventListener('orientationchange', updateOrientation)
    }
  }, [])

  return {
    isPortrait: orientation === 'portrait',
    isLandscape: orientation === 'landscape',
    orientation
  }
}