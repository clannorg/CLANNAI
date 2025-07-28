'use client'

import { useState, useEffect, useRef } from 'react'

export default function Home() {
  const [isLogin, setIsLogin] = useState(true)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [veoUrl, setVeoUrl] = useState('')
  const typedRef = useRef(null)

  // Typed.js animation
  useEffect(() => {
    const loadTyped = async () => {
      const Typed = (await import('typed.js')).default
      
      if (typedRef.current) {
        new Typed(typedRef.current, {
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
      }
    }
    
    loadTyped()
  }, [])

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register'
    const body = isLogin 
      ? { email, password }
      : { email, password, name }

    try {
      const response = await fetch(`http://localhost:3002${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        window.location.href = '/dashboard'
      } else {
        alert(data.error || 'Authentication failed')
      }
    } catch (error) {
      alert('Network error: ' + error)
    }
  }

  const handleAnalyzeClick = () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setShowAuthModal(true)
      setIsLogin(true)
    } else {
      window.location.href = '/dashboard'
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 overflow-hidden">
      {/* Hero Section with Background */}
      <div className="relative min-h-screen">
        
        {/* Background Video/Gradient */}
        <div className="absolute inset-0">
          {/* For now using gradient, can add video later */}
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-green-900/20 to-gray-900"></div>
          <div
            className="absolute inset-0"
            style={{
              background: 'linear-gradient(to bottom, rgba(17,24,39,0.3) 0%, rgba(17,24,39,0.2) 50%, rgba(17,24,39,0.8) 100%)'
            }}
          />
        </div>

        {/* Hero Content */}
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Spacer */}
          <div className="h-[35vh]"></div>

          {/* Main Hero Text */}
          <div className="text-center mb-52">
            <h1 className="text-5xl md:text-7xl font-bold text-white">
              ClannAI can now track
              <br />
              <div style={{ height: '1.2em', position: 'relative' }} className="flex justify-center">
                <span 
                  ref={typedRef}
                  className="text-green-400 text-5xl md:text-7xl"
                />
              </div>
            </h1>
            <p className="text-gray-400 text-xl mt-6">
              Transform footage into winning game insights
            </p>
          </div>

          {/* VEO Input Section */}
          <div className="relative max-w-2xl mx-auto mb-24">
            <div className="relative bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
              <div className="space-y-4">
                <input
                  type="text"
                  value={veoUrl}
                  onChange={(e) => setVeoUrl(e.target.value)}
                  placeholder="e.g. https://app.veo.co/matches/527e6a4e-f323-4524..."
                  className="w-full bg-gray-900/50 text-white px-4 py-3 rounded-lg border border-gray-700/50 
                            focus:border-green-500/50 focus:ring-2 focus:ring-green-500/20 focus:outline-none"
                />
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-400">
                    Paste your game footage URL from Veo, Trace, or Spiideo
                  </p>
                  <button 
                    onClick={handleAnalyzeClick}
                    className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-8 
                               rounded-lg transition-colors focus:outline-none focus:ring-2 
                               focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                  >
                    Analyze
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Features Showcase */}
          <div className="max-w-7xl mx-auto px-4 pt-8 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-white mb-4">Track Without GPS Devices</h2>
              <p className="text-gray-300 text-lg max-w-2xl mx-auto">
                Get metrics for both <span className="text-green-400 font-semibold">your team</span> and{' '}
                <span className="text-blue-400 font-semibold">your opponent</span> from just your match footage.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
              {/* Free Trial */}
              <div className="bg-gray-800/50 rounded-xl p-8 border border-gray-700/50 hover:border-green-500/30 transition-all">
                <div className="inline-block bg-green-500/10 text-green-400 px-4 py-1 rounded-full text-sm font-medium mb-4">
                  FREE TRIAL
                </div>
                <h3 className="text-2xl font-bold text-white mb-6">Get Started</h3>
                <ul className="text-gray-300 space-y-4 mb-8">
                  <li className="flex items-center gap-3">
                    <span className="text-green-400 text-xl">✓</span>
                    First Game Analysis
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="text-green-400 text-xl">✓</span>
                    Team Position Tracking
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="text-green-400 text-xl">✓</span>
                    Full Feature Access
                  </li>
                </ul>
                <button
                  onClick={() => { setShowAuthModal(true); setIsLogin(false) }}
                  className="w-full px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-colors"
                >
                  Start Free Trial
                </button>
              </div>

              {/* Team Analysis */}
              <div className="bg-gray-800/50 rounded-xl p-8 border border-gray-700/50">
                <div className="text-4xl mb-4">📈</div>
                <h3 className="text-xl font-bold text-white mb-3">Team Position Tracking</h3>
                <p className="text-gray-400">Real-time tactical positioning analysis and heat mapping</p>
              </div>

              {/* Sprint Analysis */}
              <div className="bg-gray-800/50 rounded-xl p-8 border border-gray-700/50">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-xl font-bold text-white mb-3">Sprint Analysis</h3>
                <p className="text-gray-400">Automatic sprint detection and energy expenditure metrics</p>
              </div>
            </div>

            {/* Team Codes */}
            <div className="text-center">
              <h3 className="text-xl font-bold text-white mb-6">Demo Team Join Codes</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm max-w-4xl mx-auto">
                <div className="bg-red-900/30 p-3 rounded-lg border border-red-700/30">
                  <div className="font-bold text-white">ARS269</div>
                  <div className="text-gray-400">Arsenal FC</div>
                </div>
                <div className="bg-blue-900/30 p-3 rounded-lg border border-blue-700/30">
                  <div className="font-bold text-white">CHE277</div>
                  <div className="text-gray-400">Chelsea Youth</div>
                </div>
                <div className="bg-red-900/30 p-3 rounded-lg border border-red-700/30">
                  <div className="font-bold text-white">LIV297</div>
                  <div className="text-gray-400">Liverpool Reserves</div>
                </div>
                <div className="bg-sky-900/30 p-3 rounded-lg border border-sky-700/30">
                  <div className="font-bold text-white">MCI298</div>
                  <div className="text-gray-400">City Development</div>
                </div>
                <div className="bg-red-900/30 p-3 rounded-lg border border-red-700/30">
                  <div className="font-bold text-white">MUN304</div>
                  <div className="text-gray-400">United U21s</div>
                </div>
              </div>
              
              <div className="mt-8">
                <button
                  onClick={() => { setShowAuthModal(true); setIsLogin(true) }}
                  className="text-green-400 hover:text-green-300 underline"
                >
                  Already have an account? Sign in here
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800/95 rounded-xl p-8 border border-gray-700/50 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">
                {isLogin ? 'Sign In' : 'Create Account'}
              </h2>
              <button 
                onClick={() => setShowAuthModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              {!isLogin && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Enter your name"
                    required={!isLogin}
                  />
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your email"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your password"
                  required
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                {isLogin ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-green-400 hover:text-green-300 text-sm"
              >
                {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>

            {/* Demo Credentials */}
            <div className="mt-6 p-4 bg-gray-700/50 rounded-lg">
              <p className="text-xs text-gray-400 mb-2">Demo Credentials:</p>
              <p className="text-xs text-gray-300">User: arsenal@demo.com / demo123</p>
              <p className="text-xs text-gray-300">Company: admin@clann.ai / demo123</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
