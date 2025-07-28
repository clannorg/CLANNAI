import Image from 'next/image'

export default function Privacy() {
  return (
    <div className="min-h-screen bg-gray-900 relative overflow-hidden">
      {/* Background Video */}
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
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(to bottom, rgba(17,24,39,0.3) 0%, rgba(17,24,39,0.2) 50%, rgba(17,24,39,0.8) 100%)'
          }}
        />
      </div>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gray-800/0 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="cursor-pointer">
              <a href="/">
                <Image
                  src="/clann-logo-white.png"
                  alt="ClannAI"
                  width={120}
                  height={28}
                  className="h-7 w-auto"
                  priority
                />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="relative z-10 pt-24">
        <div className="max-w-4xl mx-auto px-8 py-16">
          <div className="bg-gray-800/90 backdrop-blur-md rounded-xl p-8 border border-gray-700/30 shadow-2xl text-white">
            <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
            <div className="prose prose-invert max-w-none">
              
              <p className="text-gray-300 mb-6">
                <strong>Last updated:</strong> January 2025
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">1. Information We Collect</h2>
              <p className="text-gray-300 mb-4">
                We collect information you provide directly to us, such as when you create an account, 
                upload match footage, or contact us for support.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">2. How We Use Your Information</h2>
              <ul className="text-gray-300 mb-4 space-y-2">
                <li>• Provide and improve our football analysis services</li>
                <li>• Process your match footage and generate insights</li>
                <li>• Communicate with you about your account and our services</li>
                <li>• Ensure platform security and prevent fraud</li>
              </ul>

              <h2 className="text-2xl font-bold mt-8 mb-4">3. Information Sharing</h2>
              <p className="text-gray-300 mb-4">
                We do not sell, trade, or rent your personal information to third parties. 
                We may share information in certain limited circumstances, such as with your consent 
                or to comply with legal obligations.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">4. Data Security</h2>
              <p className="text-gray-300 mb-4">
                We implement appropriate technical and organizational measures to protect your 
                personal information against unauthorized access, alteration, disclosure, or destruction.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">5. Your Rights</h2>
              <p className="text-gray-300 mb-4">
                You have the right to access, update, or delete your personal information. 
                You may also opt out of certain communications from us.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">6. Contact Us</h2>
              <p className="text-gray-300 mb-4">
                If you have any questions about this Privacy Policy, please contact us at:
                <br />
                <span className="font-medium">privacy@clann.ai</span>
              </p>

              <div className="mt-12 pt-8 border-t border-gray-700">
                <a 
                  href="/"
                  className="text-green-400 hover:text-green-300 transition-colors"
                >
                  ← Back to ClannAI
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 