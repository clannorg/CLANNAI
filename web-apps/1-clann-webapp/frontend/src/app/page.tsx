'use client'

import { useState, useEffect, useRef } from 'react'
import Image from 'next/image'

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

  const openSignIn = () => {
    setIsLogin(true)
    setShowAuthModal(true)
  }

  const openSignUp = () => {
    setIsLogin(false)
    setShowAuthModal(true)
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
                width={120}
                height={28}
                className="h-7 w-auto"
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
                onClick={openSignUp}
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
                    onClick={openSignUp}
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
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800/95 backdrop-blur-sm rounded-xl p-8 border border-gray-700/50 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">
                {isLogin ? 'Sign In' : 'Create Account'}
              </h2>
              <button 
                onClick={() => setShowAuthModal(false)}
                className="text-gray-400 hover:text-white text-2xl transition-colors"
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
                    className="w-full px-3 py-3 bg-gray-700/70 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
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
                  className="w-full px-3 py-3 bg-gray-700/70 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
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
                  className="w-full px-3 py-3 bg-gray-700/70 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
                  placeholder="Enter your password"
                  required
                />
              </div>
              
              <button
                type="submit"
                className="w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
                style={{ 
                  backgroundColor: 'var(--clann-green)',
                  color: 'white'
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#015928'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--clann-green)'}
              >
                {isLogin ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-sm transition-colors"
                style={{ color: 'var(--clann-bright-green)' }}
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
