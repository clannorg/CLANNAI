import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactPlayer from 'react-player';
import userService from '../services/userService';
import activityImg from '../static/team_0_activity.png';
import heatmapImg from '../static/heatmap_team_0.png';
import sprintsImg from '../static/sprint_diagram_team_0_distance.png';
import clannLogo from '../assets/images/clann.ai-white.png';
import veoTraceImg from '../assets/images/veo-trace-spiideo.png';
import Typed from 'typed.js';
import SpiderChart from '../components/SpiderChart';
import SessionCard from '../components/SessionCard';
import clannPositionImg from '../static/clann-position.png';
import TopNav from '../components/navigation/TopNav';
import LoginSpiderChart from '../components/LoginSpiderChart';

function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const el = useRef(null);

  useEffect(() => {
    const typed = new Typed(el.current, {
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
    });

    return () => {
      typed.destroy();
    };
  }, []);

  const handleAuthClick = (isLoginMode) => {
    setIsLogin(isLoginMode);
    setShowForm(true);
    setError(null);
  };

  const handleClose = () => {
    setShowForm(false);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isLogin) {
        // Login flow
        const response = await userService.validateUser(email, password);
        console.log('Login response:', response);
        localStorage.setItem('user', JSON.stringify(response));
        navigate(response.role === 'COMPANY_MEMBER' ? '/company' : '/dashboard');
      } else {
        // Registration flow
        if (!termsAccepted) {
          setError('You must accept the Terms & Conditions to register');
          return;
        }
        const response = await userService.createUser(email, password, termsAccepted);
        console.log('Registration response:', response);
        localStorage.setItem('user', JSON.stringify(response));
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAnalyzeClick = () => {
    if (!localStorage.getItem('token')) {
      setShowForm(true);
      setIsLogin(true);
    } else {
      navigate('/dashboard');
    }
  };

  // Demo data
  const demoSession = {
    id: "demo-session",
    team_name: "Home",
    team_color: '#D1FB7A',
    opponent_color: '#B9E8EB',
    footage_url: "Match Analysis Demo",
    created_at: new Date().toISOString(),
    status: "COMPLETED",
    match_info: {
      score: {
        team1: 3,
        team2: 1
      },
      team1: {
        name: "Home",
        metrics: {
          energy: 23692,
          total_sprints: 83,
          total_distance: 75.5,
          sprint_distance: 1200,
          avg_sprint_speed: 10.4
        }
      },
      team2: {
        name: "Away",
        metrics: {
          energy: 25638,
          total_sprints: 90,
          total_distance: 82.3,
          sprint_distance: 1350,
          avg_sprint_speed: 9.8
        }
      }
    }
  };

  // Add this demo data
  const demoMetrics = {
    match_info: {
      score: { team1: 3, team2: 1 },
      team1: {
        name: "Home",
        color: '#D1FB7A',
        metrics: {
          energy: 23692,
          total_sprints: 83,
          total_distance: 75.5,
          sprint_distance: 1200,
          avg_sprint_speed: 10.4
        }
      },
      team2: {
        name: "Away",
        color: '#B9E8EB',
        metrics: {
          energy: 25638,
          total_sprints: 90,
          total_distance: 82.3,
          sprint_distance: 1350,
          avg_sprint_speed: 9.8
        }
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 relative overflow-hidden">
      {/* Background Demo Section - Positioned absolutely */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
          {/* Repeat these blocks to fill the background */}
          <div className="transform rotate-3">
            <SessionCard session={demoSession} />
          </div>
          <div className="transform -rotate-2">
            <SpiderChart sessionData={demoSession} />
          </div>
          <div className="transform rotate-1">
            <SessionCard session={{...demoSession, team_name: "St. Mary's GAA"}} />
          </div>
          <div className="transform -rotate-3">
            <SpiderChart sessionData={demoSession} />
          </div>
        </div>
      </div>

      {/* Gradient Overlay */}
      <div 
        className="absolute inset-0 z-10"
        style={{
          background: 'linear-gradient(to bottom, rgba(17,24,39,0.95) 0%, rgba(17,24,39,0.8) 50%, rgba(17,24,39,0.95) 100%)'
        }}
      />

      {/* Main Content - On top of background */}
      <div className="relative z-20">
        <div className="relative min-h-screen">
          <div className="relative z-10">
            {/* Hero Video Background - Fixed Position */}
            <div className="fixed inset-0 w-full h-full -z-10">
              <video
                autoPlay
                loop
                muted
                playsInline
                className="absolute inset-0 w-full h-full object-cover opacity-80"
              >
                <source src="/videos/hero-video.mp4" type="video/mp4" />
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
              {/* Empty space - reduced */}
              <div className="h-[35vh]"></div>

              {/* Text Section */}
              <div className="text-center mb-52">
                <h1 className="text-5xl md:text-7xl font-bold text-white">
                  ClannAI can now track
                  <br />
                  <div style={{ height: '1.2em', position: 'relative' }} className="flex justify-center">
                    <span 
                      ref={el}
                      className="text-[#4EC2CA] text-5xl md:text-7xl"
                    />
                  </div>
                </h1>
                <p className="text-gray-400 text-xl mt-6">
                  Transform footage into winning game insights
                </p>
              </div>

              {/* Camera Image and Input Section - adjusted top position */}
              <div className="relative max-w-2xl mx-auto">
                {/* Camera Image - moved higher up */}
                <div className="absolute -top-52 left-1/2 -translate-x-1/2 w-[350px]">
                  <img
                    src={veoTraceImg}
                    alt="Camera Systems"
                    className="w-full h-auto opacity-90"
                  />
                </div>
                
                {/* Input Box - moved lower down */}
                <div className="relative bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50 mt-24">
                  <div className="space-y-4">
                    <input
                      type="text"
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
                        className="bg-[#016F32] hover:bg-[#015928] text-white font-medium py-3 px-8 
                                   rounded-lg transition-colors focus:outline-none focus:ring-2 
                                   focus:ring-[#D1FB7A] focus:ring-offset-2 focus:ring-offset-gray-900"
                      >
                        Analyze
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Metrics Comparison with Integrated Pentagon Chart */}
              <div className="mt-24 mb-12 px-4">
                <div className="flex flex-col items-center mb-12">
                  <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">Track Without GPS Devices</h2>
                  <p className="text-gray-300 text-center max-w-2xl">
                    Get metrics for both <span style={{ color: '#D1FB7A' }}>your team</span> and 
                    <span style={{ color: '#B9E8EB' }}> your opponent</span> from just your match footage.
                  </p>
                </div>

                {/* Integrated Spider Chart with Metrics */}
                <div className="max-w-3xl mx-auto">
                  <LoginSpiderChart 
                    sessionData={demoMetrics} 
                    colors={{ 
                      team1: "#D1FB7A", 
                      team2: "#B9E8EB" 
                    }} 
                  />
                </div>
              </div>

              {/* Analysis Showcase - exactly as in the original file */}
              <div className="max-w-7xl mx-auto px-4 pt-8 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {[
                    {
                      title: 'Team Position Tracking',
                      description: 'Track real-time team formations and tactical positioning throughout the match',
                      image: clannPositionImg,
                      icon: '📈'
                    },
                    {
                      title: 'Heat Mapping',
                      description: 'Visualize player positioning and movement patterns',
                      image: heatmapImg,
                      icon: '🔥'
                    },
                    {
                      title: 'Sprint Analysis',
                      description: 'Automatically detect key sprints and player movements',
                      image: sprintsImg,
                      icon: '⚡️'
                    }
                  ].map(feature => (
                    <div key={feature.title} 
                         className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 
                                  hover:border-green-500/30 transition-all transform hover:-translate-y-1">
                      <img
                        src={feature.image}
                        alt={feature.title}
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
                    <div className="inline-block bg-green-500/10 text-green-400 px-4 py-1 rounded-full text-sm font-medium mb-4">
                      STEP 1
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-6">
                      Start Your Free Trial
                    </h2>
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
                      onClick={() => handleAuthClick(false)}
                      className="w-full px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-colors"
                    >
                      Start Free Trial
                    </button>
                  </div>

                  {/* Premium */}
                  <div className="md:col-span-3 bg-gray-800/50 rounded-xl p-8 border border-gray-700/50 hover:border-blue-500/30 transition-all">
                    <div className="inline-block bg-blue-500/10 text-blue-400 px-4 py-1 rounded-full text-sm font-medium mb-4">
                      STEP 2
                    </div>
                    <h2 className="text-3xl font-bold text-white mb-6">
                      Continue with Premium
                    </h2>
                    <div className="text-4xl font-bold text-blue-400 mb-6">
                      £75/month
                    </div>
                    <div className="text-gray-300 space-y-4">
                      <div className="flex items-center gap-3">
                        <span className="text-blue-400 text-xl">✓</span>
                        Unlimited Games
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-blue-400 text-xl">✓</span>
                        Priority Analysis
                      </div>
                    </div>
                  </div>

                  {/* AI Coaching Insights */}
                  <div className="md:col-span-2 bg-gray-800/50 rounded-xl p-8 border border-gray-700/50">
                    <div className="inline-block bg-purple-500/10 text-purple-400 px-4 py-1 rounded-full text-sm font-medium mb-4">
                      COMING SOON
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-6">
                      AI Coaching
                    </h2>
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
              </div>
            </div>

            {/* Auth Modal */}
            {showForm && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-30">
                <div className="bg-gray-800/95 rounded-xl p-8 border border-gray-700/50 max-w-md w-full mx-4">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-white">
                      {isLogin ? 'Sign In' : 'Create Account'}
                    </h2>
                    <button 
                      onClick={handleClose}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>

                  {error && (
                    <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded mb-6">
                      {error}
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                      id="auth-email-input"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Email"
                      className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-3 
                               text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                    />
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-3 
                                 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400"
                      >
                        {showPassword ? '🙈' : '👁️'}
                      </button>
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 
                               rounded-lg transition-colors focus:outline-none focus:ring-2 
                               focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                    >
                      {isLogin ? 'Sign In' : 'Create Account'}
                    </button>
                  </form>

                  {!isLogin && (
                    <div className="mt-4">
                      <label className="flex items-start gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={termsAccepted}
                          onChange={(e) => setTermsAccepted(e.target.checked)}
                          className="mt-1 rounded border-gray-600 bg-gray-700 text-green-500"
                        />
                        <span className="text-sm text-gray-300">
                          I accept the <a href="/terms" className="text-green-500 hover:underline" target="_blank">Terms & Conditions</a> and
                          <a href="/privacy" className="text-green-500 hover:underline" target="_blank"> Privacy Policy</a>
                        </span>
                      </label>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <TopNav 
        onSignInClick={() => handleAuthClick(true)}
        onGetStartedClick={() => handleAuthClick(false)}
      />
    </div>
  );
}

export default Login;