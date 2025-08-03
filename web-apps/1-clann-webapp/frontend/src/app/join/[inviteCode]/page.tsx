'use client'

import { useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import apiClient from '@/lib/api-client'

export default function JoinTeamPage() {
  const router = useRouter()
  const params = useParams()
  const inviteCode = params.inviteCode as string

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      // User is already authenticated, join team directly
      joinTeam()
    } else {
      // User not authenticated, redirect to homepage with join parameters
      router.push(`/?join=${inviteCode}&autoJoin=true`)
    }
  }, [inviteCode, router])

  const joinTeam = async () => {
    try {
      const response = await apiClient.joinTeamByCode(inviteCode)
      // Redirect to dashboard after successful join
      router.push('/dashboard')
    } catch (err: any) {
      console.error('Failed to join team:', err)
      if (err.message?.includes('already a member')) {
        // Already a member, just go to dashboard
        router.push('/dashboard')
      } else {
        // Error joining, redirect to homepage with error
        router.push(`/?join=${inviteCode}&error=${encodeURIComponent(err.message || 'Failed to join team')}`)
      }
    }
  }

  // Show loading while processing
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#016F32]/5 to-[#016F32]/10">
      <div className="bg-white rounded-2xl shadow-2xl p-8 text-center">
        <div className="w-16 h-16 bg-[#016F32]/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-[#016F32] animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Processing join request...</h2>
        <p className="text-gray-600">Please wait while we process your team join request.</p>
      </div>
    </div>
  )
}