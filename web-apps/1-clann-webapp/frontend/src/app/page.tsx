'use client'

import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import Image from 'next/image'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3002'

export default function Home() {
  const searchParams = useSearchParams()
  const [isLogin, setIsLogin] = useState(true)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [veoUrl, setVeoUrl] = useState('')
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [joinCode, setJoinCode] = useState<string | null>(null)
  const [teamName, setTeamName] = useState<string | null>(null)
  const typedRef = useRef(null)

  // Typed.js animation
  useEffect(() => {
    const loadTyped = async () => {
      const Typed = (await import('typed.js')).default
      
      if (typedRef.current) {
        const typed = new Typed(typedRef.current, {
          strings: [
            'distance covered',
            'sprint speeds', 
            'defensive shape',
            'counter attacks',
            'energy expended',
            'tactical patterns',
            'game momentum'
          ],
          typeSpeed: 50,
          backSpeed: 50,
          backDelay: 1000,
          loop: true,
          showCursor: true,
          cursorChar: '|'
        })

        return () => {
          typed.destroy()
        }
      }
    }
    
    loadTyped()
  }, [])

  // Check for join parameters in URL
  useEffect(() => {
    const join = searchParams.get('join')
    const autoJoin = searchParams.get('autoJoin')
    const errorMsg = searchParams.get('error')

    if (join) {
      console.log('🔗 Join code detected in URL:', join, 'autoJoin:', autoJoin)
      setJoinCode(join)
      
      // Fetch team info for the banner
      fetchTeamInfo(join)
      
      // Auto-open auth modal if autoJoin is true OR just join code exists
      // Small delay to ensure everything is loaded
      setTimeout(() => {
        if (autoJoin === 'true' || join) {
          console.log('🎯 Auto-opening registration modal for join code:', join)
          setIsLogin(false) // Set to sign-up mode FIRST
          setShowAuthModal(true) // Then open modal
        }
      }, 100)
      
      // Show error if provided (but only if not auto-opening)
      if (errorMsg && autoJoin !== 'true') {
        setError(decodeURIComponent(errorMsg))
      }
    }
  }, [searchParams])

  const fetchTeamInfo = async (code: string) => {
    try {
      // Get demo team info to display team name
      const response = await fetch(`${API_BASE_URL}/api/teams/codes/demo`)
      const data = await response.json()
      
      const team = data.codes?.find((t: any) => t.code === code)
      if (team) {
        setTeamName(team.team)
      }
    } catch (error) {
      console.error('Failed to fetch team info:', error)
    }
  }

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    try {
      if (!isLogin && !termsAccepted) {
        setError('You must accept the Terms & Conditions to register')
        return
      }
    
    const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register'
    const body = isLogin 
      ? { email, password }
        : { 
            email, 
            password, 
            phone,
            // Auto-detect company role for @clann.ai emails
            ...(email.endsWith('@clann.ai') && { role: 'company' })
          }

              const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        // Check for join code in URL parameters first
        if (joinCode) {
          // Auto-join the team
          console.log('🎯 Attempting to join team with code:', joinCode)
          try {
            const joinResponse = await fetch(`${API_BASE_URL}/api/teams/join-by-code`, {
              method: 'POST',
              headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${data.token}`
              },
              body: JSON.stringify({ inviteCode: joinCode })
            })
            
            console.log('🔍 Join response status:', joinResponse.status)
            
            if (joinResponse.ok) {
              // Successfully joined, go to dashboard
              console.log('✅ Successfully joined team!')
              window.location.href = '/dashboard'
            } else {
              // Failed to join, still go to dashboard but show error
              const joinError = await joinResponse.json()
              console.error('❌ Failed to join team:', joinError)
              window.location.href = `/dashboard?error=${encodeURIComponent(joinError.error || 'Failed to join team')}`
            }
          } catch (error) {
            // Error joining, go to dashboard
            console.error('🚨 Error during join process:', error)
            window.location.href = `/dashboard?error=${encodeURIComponent('Failed to join team')}`
          }
        } else {
          // Check for legacy pending invite code
          const pendingInviteCode = localStorage.getItem('pendingInviteCode')
          if (pendingInviteCode) {
            localStorage.removeItem('pendingInviteCode')
            window.location.href = `/join/${pendingInviteCode}`
          } else {
            window.location.href = '/dashboard'
          }
        }
      } else {
        setError(data.error || 'Authentication failed')
      }
    } catch (error) {
      setError('Network error: ' + error)
    }
  }

  const handleAnalyzeClick = () => {
    const token = localStorage.getItem('token')
    if (!token) {
      openGetStarted()
    } else {
      window.location.href = '/dashboard'
    }
  }

  const openSignIn = () => {
    setIsLogin(true)
    setShowAuthModal(true)
    setError(null)
  }

  const openSignUp = () => {
    setIsLogin(false)
    setShowAuthModal(true)
    setError(null)
  }

  const openGetStarted = () => {
    // If there's a join code, open in sign-up mode
    if (joinCode) {
      setIsLogin(false)
    } else {
      setIsLogin(false) // Default to sign-up for new users
    }
    setShowAuthModal(true)
    setError(null)
  }

  const handleClose = () => {
    setShowAuthModal(false)
    setError(null)
  }
  

  return (
    <div className="min-h-screen bg-gray-900 relative overflow-hidden">
      <style jsx global>{`
        :root {
          --clann-green: #016F32;
          --clann-blue: #4EC2CA;
          --clann-bright-green: #D1FB7A;
          --clann-light-blue: #B9E8EB;
        }
      `}</style>

      {/* Header Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gray-800/0 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex justify-between items-center">
            {/* Logo */}
            <div className="cursor-pointer">
              <Image
                src="/clann-logo-white.png"
                alt="ClannAI"
                width={180}
                height={48}
                className="h-12 w-auto"
                priority
              />
          </div>

            {/* Auth Buttons */}
            <div className="flex items-center gap-6">
              <button
                onClick={openSignIn}
                className="text-white text-base font-medium hover:text-gray-300 px-6 py-2.5 text-[15px]"
              >
                Sign in
              </button>
              <button
                onClick={openGetStarted}
                className="bg-black px-6 py-2.5 rounded-lg text-base font-medium text-white hover:bg-gray-900 text-[15px]"
              >
                Get started
              </button>
            </div>
            </div>
            </div>
      </header>



      {/* Main Content Container */}
      <div className="relative z-10">
        <div className="relative min-h-screen">
          
          {/* Hero Video Background - Fixed Position */}
          <div className="fixed inset-0 w-full h-full -z-10">
            <video
              autoPlay
              loop
              muted
              playsInline
              className="absolute inset-0 w-full h-full object-cover opacity-80"
            >
              <source src="/hero-video.mp4" type="video/mp4" />
            </video>

            {/* Gradient Overlay */}
            <div
              className="absolute inset-0"
              style={{
                background: 'linear-gradient(to bottom, rgba(17,24,39,0.3) 0%, rgba(17,24,39,0.2) 50%, rgba(17,24,39,0.8) 100%)'
              }}
            />
          </div>

          {/* Hero Content */}
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            
            {/* Empty space above hero text */}
            <div className="h-[35vh]"></div>

            {/* Hero Text Section */}
            <div className="text-center mb-52">
              <h1 className="text-5xl md:text-7xl font-bold text-white">
                ClannAI can now track
                <br />
                <div style={{ height: '1.2em', position: 'relative' }} className="flex justify-center">
                  <span 
                    ref={typedRef}
                    className="text-5xl md:text-7xl font-bold"
                    style={{ color: 'var(--clann-bright-green)' }}
                  />
                </div>
              </h1>
              <p className="text-gray-400 text-xl mt-6">
                Transform footage into winning game insights
              </p>
            </div>

            {/* Platform Integration & VEO Input Section */}
            <div className="relative max-w-2xl mx-auto">
              {/* Platform Logos - Positioned absolutely above input */}
              <div className="absolute -top-52 left-1/2 -translate-x-1/2 w-[350px]">
                <Image
                  src="/veo-trace-spiideo.png"
                  alt="Supported Platforms: Veo, Trace, Spiideo"
                  width={350}
                  height={100}
                  className="w-full h-auto opacity-90"
                />
              </div>
              
              {/* VEO Input Box - Positioned with proper spacing */}
              <div className="relative bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50 shadow-2xl mt-24">
                <div className="space-y-4">
                  <input
                    type="text"
                    value={veoUrl}
                    onChange={(e) => setVeoUrl(e.target.value)}
                    placeholder="e.g. https://app.veo.co/matches/527e6a4e-f323-4524..."
                    className="w-full bg-gray-900/50 text-white px-4 py-3 rounded-lg border border-gray-700/50 focus:border-green-500/50 focus:ring-2 focus:ring-green-500/20 focus:outline-none placeholder-gray-400"
                  />
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <p className="text-sm text-gray-400">
                      Paste your game footage URL from Veo, Trace, or Spiideo
                    </p>
                    <button 
                      onClick={handleAnalyzeClick}
                      className="px-8 py-3 rounded-lg font-medium text-white transition-all duration-200 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900"
                      style={{ 
                        backgroundColor: 'var(--clann-green)',
                        boxShadow: '0 4px 20px rgba(1, 111, 50, 0.3)'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#015928'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--clann-green)'}
                    >
                      Analyze
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Features Section Header */}
            <div className="mt-24 mb-12 px-4">
              <div className="flex flex-col items-center mb-12">
                <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">Track Without GPS Devices</h2>
                <p className="text-gray-300 text-center max-w-2xl">
                  Get metrics for both <span className="font-semibold" style={{ color: 'var(--clann-bright-green)' }}>your team</span> and{' '}
                  <span className="font-semibold" style={{ color: 'var(--clann-light-blue)' }}>your opponent</span> from just your match footage.
                </p>
              </div>
            </div>

            {/* Analysis Showcase Grid */}
            <div className="max-w-7xl mx-auto px-4 pt-8 sm:px-6 lg:px-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                  {
                    title: 'Team Position Tracking',
                    description: 'Track real-time team formations and tactical positioning throughout the match',
                    image: '/clann-position.png',
                    icon: '📈'
                  },
                  {
                    title: 'Heat Mapping',
                    description: 'Visualize player positioning and movement patterns',
                    image: '/heatmap_team_0.png',
                    icon: '🔥'
                  },
                  {
                    title: 'Sprint Analysis',
                    description: 'Automatically detect key sprints and player movements',
                    image: '/sprint_diagram_team_0_distance.png',
                    icon: '⚡️'
                  }
                ].map(feature => (
                  <div key={feature.title} 
                       className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-green-500/30 transition-all transform hover:-translate-y-1">
                    <Image
                      src={feature.image}
                      alt={feature.title}
                      width={300}
                      height={200}
                      className="w-full h-auto object-contain rounded-lg bg-black/30 mb-6"
                    />
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-2xl">{feature.icon}</span>
                      <h3 className="text-xl font-bold text-white">{feature.title}</h3>
                    </div>
                    <p className="text-gray-400">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Pricing & Call to Action */}
            <div className="max-w-4xl mx-auto px-4 pt-24 pb-24">
              <div className="grid grid-cols-1 md:grid-cols-7 gap-8">
                
                {/* Free Trial */}
                <div className="md:col-span-2 bg-gray-800/50 rounded-xl p-8 border border-gray-700/50 hover:border-green-500/30 transition-all">
                  <div className="inline-block px-4 py-1 rounded-full text-sm font-medium mb-4"
                       style={{ 
                         backgroundColor: 'rgba(209, 251, 122, 0.1)',
                         color: 'var(--clann-bright-green)'
                       }}>
                    STEP 1
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-6">Start Your Free Trial</h2>
                  <ul className="text-gray-300 space-y-4 mb-8">
                    <li className="flex items-center gap-3">
                      <span className="text-xl" style={{ color: 'var(--clann-bright-green)' }}>✓</span>
                      First Game Analysis
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-xl" style={{ color: 'var(--clann-bright-green)' }}>✓</span>
                      Team Position Tracking
                    </li>
                    <li className="flex items-center gap-3">
                      <span className="text-xl" style={{ color: 'var(--clann-bright-green)' }}>✓</span>
                      Full Feature Access
                    </li>
                  </ul>
                  <button
                    onClick={openGetStarted}
                    className="w-full px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
                    style={{ 
                      backgroundColor: 'var(--clann-green)',
                      color: 'white'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#015928'}
                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--clann-green)'}
                  >
                    Start Free Trial
                  </button>
                </div>

                {/* Premium */}
                <div className="md:col-span-3 bg-gray-800/50 rounded-xl p-8 border border-gray-700/50 hover:border-blue-500/30 transition-all">
                  <div className="inline-block px-4 py-1 rounded-full text-sm font-medium mb-4"
                       style={{ 
                         backgroundColor: 'rgba(78, 194, 202, 0.1)',
                         color: 'var(--clann-blue)'
                       }}>
                    STEP 2
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-6">Continue with Premium</h2>
                  <div className="text-4xl font-bold mb-6" style={{ color: 'var(--clann-blue)' }}>
                    £75/month
                  </div>
                  <div className="text-gray-300 space-y-4">
                    <div className="flex items-center gap-3">
                      <span className="text-xl" style={{ color: 'var(--clann-blue)' }}>✓</span>
                      Unlimited Games
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xl" style={{ color: 'var(--clann-blue)' }}>✓</span>
                      Priority Analysis
                    </div>
                  </div>
                </div>

                {/* AI Coaching Insights */}
                <div className="md:col-span-2 bg-gray-800/50 rounded-xl p-8 border border-gray-700/50">
                  <div className="inline-block bg-purple-500/10 text-purple-400 px-4 py-1 rounded-full text-sm font-medium mb-4">
                    COMING SOON
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-6">AI Coaching</h2>
                  <div className="space-y-6">
                    <div className="text-gray-400">
                      <div className="flex items-center gap-3">
                        <span className="text-purple-400 text-xl">✓</span>
                        Tactical Recommendations
                      </div>
                    </div>
                    <div className="text-gray-400">
                      <div className="flex items-center gap-3">
                        <span className="text-purple-400 text-xl">✓</span>
                        Counter-Attack Analysis
                      </div>
                    </div>
                    <div className="text-gray-400">
                      <div className="flex items-center gap-3">
                        <span className="text-purple-400 text-xl">✓</span>
                        Formation Optimization
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Team Codes */}
              <div className="text-center mt-16">
                <h3 className="text-xl font-bold text-white mb-6">Demo Team Join Codes</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm max-w-4xl mx-auto">
                  <div className="bg-red-900/40 backdrop-blur-sm p-4 rounded-lg border border-red-700/30 hover:border-red-500/50 transition-all">
                    <div className="font-bold text-white">ARS269</div>
                    <div className="text-gray-400">Arsenal FC</div>
                  </div>
                  <div className="bg-blue-900/40 backdrop-blur-sm p-4 rounded-lg border border-blue-700/30 hover:border-blue-500/50 transition-all">
                    <div className="font-bold text-white">CHE277</div>
                    <div className="text-gray-400">Chelsea Youth</div>
                  </div>
                  <div className="bg-red-900/40 backdrop-blur-sm p-4 rounded-lg border border-red-700/30 hover:border-red-500/50 transition-all">
                    <div className="font-bold text-white">LIV297</div>
                    <div className="text-gray-400">Liverpool Reserves</div>
                  </div>
                  <div className="bg-sky-900/40 backdrop-blur-sm p-4 rounded-lg border border-sky-700/30 hover:border-sky-500/50 transition-all">
                    <div className="font-bold text-white">MCI298</div>
                    <div className="text-gray-400">City Development</div>
                  </div>
                  <div className="bg-red-900/40 backdrop-blur-sm p-4 rounded-lg border border-red-700/30 hover:border-red-500/50 transition-all">
                    <div className="font-bold text-white">MUN304</div>
                    <div className="text-gray-400">United U21s</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800/50 backdrop-blur-sm border-t border-gray-700/50 mt-24">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <Image
                src="/clann-logo-white.png"
                alt="ClannAI"
                width={100}
                height={24}
                className="h-6 w-auto"
              />
              <span className="ml-3 text-gray-400 text-sm">
                © 2025 ClannAI. All rights reserved.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a 
                href="/privacy" 
                className="text-gray-400 hover:text-white text-sm transition-colors"
              >
                Privacy Policy
              </a>
              <a 
                href="/terms" 
                className="text-gray-400 hover:text-white text-sm transition-colors"
              >
                Terms of Service
              </a>
              <a 
                href="mailto:contact@clann.ai" 
                className="text-gray-400 hover:text-white text-sm transition-colors"
              >
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 flex items-center justify-center z-30" style={{ pointerEvents: 'none' }}>
                     <div className="rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl" style={{ backgroundColor: 'rgba(0, 0, 0, 0.95)', border: '1px solid rgba(75, 85, 99, 0.5)', pointerEvents: 'auto' }}>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-semibold text-white">
                {isLogin ? 'Sign In' : 'Create Account'}
              </h2>
                              <button 
                  onClick={handleClose}
                  className="text-gray-400 hover:text-white w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/50 transition-all"
                >
                ✕
              </button>
            </div>

            {/* Join Team Message */}
            {joinCode && (
              <div className="bg-[#016F32]/10 border border-[#016F32]/30 text-[#D1FB7A] px-5 py-4 rounded-xl mb-6 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-[#016F32]/20 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-[#D1FB7A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.196-2.121M9 6a3 3 0 106 0 3 3 0 00-6 0zM12 14a6 6 0 00-6 6v2h12v-2a6 6 0 00-6-6z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium">You'll automatically join {teamName || 'the team'}</p>
                    <p className="text-sm text-white/60">Team code: {joinCode}</p>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-5 py-4 rounded-xl mb-6 backdrop-blur-sm">
                {error}
                </div>
              )}
              
            <form onSubmit={handleAuthSubmit} className="space-y-5">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                  className="w-full rounded-xl px-5 py-4 text-white placeholder-gray-400 focus:outline-none transition-all"
                  style={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.6)', 
                    border: '1px solid rgba(75, 85, 99, 0.5)'
                  }}
                  onFocus={(e) => e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.8)'}
                  onBlur={(e) => e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.6)'}
                  required
                />
              
              {!isLogin && (
                                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="Phone Number (Optional)"
                    className="w-full rounded-xl px-5 py-4 text-white placeholder-gray-400 focus:outline-none transition-all"
                    style={{ 
                      backgroundColor: 'rgba(0, 0, 0, 0.6)', 
                      border: '1px solid rgba(75, 85, 99, 0.5)'
                    }}
                    onFocus={(e) => e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.8)'}
                    onBlur={(e) => e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.6)'}
                  />
              )}
              
              <div className="relative">
                <input
                    type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    className="w-full rounded-xl px-5 py-4 text-white placeholder-gray-400 focus:outline-none transition-all"
                    style={{ 
                      backgroundColor: 'rgba(0, 0, 0, 0.6)', 
                      border: '1px solid rgba(75, 85, 99, 0.5)'
                    }}
                    onFocus={(e) => e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.8)'}
                    onBlur={(e) => e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.6)'}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-300 transition-colors"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
              
              <button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-500 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 hover:shadow-lg hover:shadow-green-500/25 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:ring-offset-2 focus:ring-offset-gray-900 mt-6"
                style={{ backgroundColor: 'var(--clann-green)' }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#015928'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--clann-green)'}
              >
                {isLogin ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            {!isLogin && (
              <div className="mt-6">
                <label className="flex items-start gap-3 cursor-pointer">
                                      <input
                      type="checkbox"
                      checked={termsAccepted}
                      onChange={(e) => setTermsAccepted(e.target.checked)}
                      className="mt-1 rounded border-gray-800 bg-black text-green-500 focus:ring-green-500/30"
                    />
                  <span className="text-sm text-gray-300 leading-relaxed">
                    I accept the <a href="/terms" className="text-green-400 hover:text-green-300 transition-colors" target="_blank">Terms & Conditions</a> and
                    <a href="/privacy" className="text-green-400 hover:text-green-300 transition-colors" target="_blank"> Privacy Policy</a>
                  </span>
                </label>
              </div>
            )}

            <div className="mt-8 text-center">
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-sm text-green-400 hover:text-green-300 transition-colors font-medium"
              >
                {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>

            {/* Demo Credentials */}
            <div className="mt-6 p-4 bg-black/40 rounded-xl border border-gray-800/30">
              <p className="text-xs text-gray-400 mb-3 font-medium">Demo Credentials:</p>
              <div className="space-y-1">
                              <p className="text-xs text-gray-300">Company: admin@clann.ai / demo123</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
