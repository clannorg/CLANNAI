'use client'

import { useState } from 'react'

export default function Home() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 to-gray-900">
      {/* Hero Section */}
      <div className="relative">
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div className="relative z-10 px-4 py-16">
          <div className="max-w-6xl mx-auto text-center">
            <h1 className="text-6xl font-bold text-white mb-6">
              ClannAI
            </h1>
            <p className="text-2xl text-green-300 mb-8">
              AI-Powered Football Analysis Platform
            </p>
            <div className="text-xl text-gray-300 mb-12">
              Analyze <span className="text-green-400 font-semibold">counter attacks</span>, 
              track <span className="text-green-400 font-semibold">player positioning</span>, 
              measure <span className="text-green-400 font-semibold">energy expended</span>
            </div>
          </div>

          {/* Features Grid */}
          <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-bold text-white mb-3">Team Position Tracking</h3>
              <p className="text-gray-400">Real-time tactical positioning analysis</p>
            </div>
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
              <div className="text-4xl mb-4">🔥</div>
              <h3 className="text-xl font-bold text-white mb-3">Heat Mapping</h3>
              <p className="text-gray-400">Visualize player movement patterns</p>
            </div>
            <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-bold text-white mb-3">Sprint Analysis</h3>
              <p className="text-gray-400">Automatic sprint detection and metrics</p>
            </div>
          </div>

          {/* Auth Form */}
          <div className="max-w-md mx-auto bg-gray-800/80 rounded-xl p-8 backdrop-blur-sm border border-gray-700">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">
                {isLogin ? 'Sign In' : 'Create Account'}
              </h2>
              <p className="text-gray-400">
                {isLogin ? 'Access your team analysis' : 'Start analyzing your team'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
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
                className="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
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

          {/* Team Codes */}
          <div className="max-w-4xl mx-auto mt-16 text-center">
            <h3 className="text-xl font-bold text-white mb-4">Team Join Codes</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              <div className="bg-red-900/30 p-3 rounded-lg">
                <div className="font-bold text-white">ARS269</div>
                <div className="text-gray-400">Arsenal FC</div>
              </div>
              <div className="bg-blue-900/30 p-3 rounded-lg">
                <div className="font-bold text-white">CHE277</div>
                <div className="text-gray-400">Chelsea Youth</div>
              </div>
              <div className="bg-red-900/30 p-3 rounded-lg">
                <div className="font-bold text-white">LIV297</div>
                <div className="text-gray-400">Liverpool Reserves</div>
              </div>
              <div className="bg-sky-900/30 p-3 rounded-lg">
                <div className="font-bold text-white">MCI298</div>
                <div className="text-gray-400">City Development</div>
              </div>
              <div className="bg-red-900/30 p-3 rounded-lg">
                <div className="font-bold text-white">MUN304</div>
                <div className="text-gray-400">United U21s</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
