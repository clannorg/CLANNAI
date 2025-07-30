'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import apiClient from '@/lib/api-client'

export default function JoinTeamPage() {
  const router = useRouter()
  const params = useParams()
  const inviteCode = params.inviteCode as string
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [teamInfo, setTeamInfo] = useState<any>(null)
  const [user, setUser] = useState<any>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
      setIsAuthenticated(true)
      joinTeam()
    } else {
      setIsAuthenticated(false)
      setLoading(false)
    }
  }, [inviteCode, router])

  const joinTeam = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await apiClient.joinTeamByCode(inviteCode)
      
      setTeamInfo(response.team)
      setSuccess(true)
      
      // Redirect to dashboard after 3 seconds
      setTimeout(() => {
        router.push('/dashboard')
      }, 3000)
      
    } catch (err: any) {
      console.error('Failed to join team:', err)
      if (err.message?.includes('already a member')) {
        setError('You are already a member of this team')
      } else {
        setError(err.message || 'Failed to join team')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSignIn = () => {
    localStorage.setItem('pendingInviteCode', inviteCode)
    router.push('/')
  }

  // Authentication required screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#016F32]/5 to-[#016F32]/10 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-[#016F32] to-[#014d24] p-6 text-center">
            <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4 backdrop-blur-sm">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Authentication Required</h1>
            <p className="text-white/80 text-sm">You need to sign in to join a team</p>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            <div className="text-center p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div className="w-12 h-12 bg-[#016F32]/10 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-[#016F32]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.196-2.121M9 6a3 3 0 106 0 3 3 0 00-6 0zM12 14a6 6 0 00-6 6v2h12v-2a6 6 0 00-6-6z" />
                </svg>
              </div>
              <h3 className="font-bold text-lg text-gray-900 mb-2">Join Team Invitation</h3>
              <p className="text-sm text-gray-600 mb-3">
                You've been invited to join a team using invite code:
              </p>
              <div className="bg-[#016F32] text-white px-3 py-1 rounded-lg font-mono text-sm font-bold inline-block">
                {inviteCode}
              </div>
              <p className="text-xs text-gray-500 mt-3">
                Please sign in to verify and accept this invitation.
              </p>
            </div>

            <div className="space-y-3">
              <button
                onClick={handleSignIn}
                className="w-full bg-[#016F32] text-white py-3 px-4 rounded-xl font-semibold hover:bg-[#014d24] transition-all duration-200 transform hover:scale-[1.02] shadow-lg"
              >
                Sign In to Continue
              </button>
              
              <button
                onClick={() => router.push('/dashboard')}
                className="w-full border border-gray-300 text-gray-700 py-3 px-4 rounded-xl font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Loading screen
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#016F32]/5 to-[#016F32]/10 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
          <div className="text-center">
            <div className="w-20 h-20 bg-[#016F32]/10 rounded-full flex items-center justify-center mx-auto mb-6 relative">
              <div className="absolute inset-0 rounded-full border-4 border-[#016F32]/20 animate-pulse"></div>
              <div className="w-8 h-8 border-4 border-[#016F32] border-t-transparent rounded-full animate-spin"></div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Joining Team...</h2>
            <p className="text-gray-600">Please wait while we process your invitation</p>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
              <div className="bg-[#016F32] h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error screen
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-red-100 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
          <div className="p-8 text-center">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-200">
              <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              {error.includes('already a member') ? 'Already a Member' : 'Invalid Invite'}
            </h2>
            <p className="text-gray-600 mb-6 leading-relaxed">{error}</p>
            <div className="space-y-3">
              <Link
                href="/dashboard"
                className="inline-block w-full bg-[#016F32] text-white py-3 px-6 rounded-xl font-semibold hover:bg-[#014d24] transition-all duration-200 transform hover:scale-[1.02]"
              >
                {error.includes('already a member') ? 'Go to Dashboard' : 'Back to Dashboard'}
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Success screen
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
          <div className="p-8 text-center">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 border border-green-200 relative">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
              <div className="absolute inset-0 rounded-full border-4 border-green-200 animate-ping opacity-20"></div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">🎉 Welcome to the Team!</h2>
            <p className="text-gray-600 mb-2">You've successfully joined:</p>
            <div className="bg-[#016F32]/10 rounded-xl p-4 mb-6">
              <p className="text-2xl font-bold text-[#016F32] mb-1">{teamInfo?.name}</p>
              <p className="text-sm text-gray-600">Team Code: {teamInfo?.invite_code}</p>
            </div>
            <div className="flex items-center justify-center text-sm text-gray-500">
              <svg className="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Redirecting to dashboard...
            </div>
          </div>
        </div>
      </div>
    )
  }

  return null
} 