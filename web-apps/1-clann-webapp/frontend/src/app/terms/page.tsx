import Image from 'next/image'

export default function Terms() {
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
            <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
            <div className="prose prose-invert max-w-none">
              
              <p className="text-gray-300 mb-6">
                <strong>Last updated:</strong> January 2025
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-300 mb-4">
                By accessing and using ClannAI's services, you accept and agree to be bound by 
                the terms and provision of this agreement.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">2. Service Description</h2>
              <p className="text-gray-300 mb-4">
                ClannAI provides AI-powered football analysis services, including match footage 
                processing, player tracking, tactical analysis, and performance insights.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">3. User Accounts</h2>
              <ul className="text-gray-300 mb-4 space-y-2">
                <li>• You must provide accurate information when creating an account</li>
                <li>• You are responsible for maintaining the security of your account</li>
                <li>• You must not share your account credentials</li>
                <li>• One account per user</li>
              </ul>

              <h2 className="text-2xl font-bold mt-8 mb-4">4. Acceptable Use</h2>
              <p className="text-gray-300 mb-4">
                You agree to use our services only for lawful purposes and in accordance with these Terms. 
                You must not upload content that infringes on others' rights or violates any laws.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">5. Payment Terms</h2>
              <ul className="text-gray-300 mb-4 space-y-2">
                <li>• Free trial available for new users</li>
                <li>• Premium subscription: £75/month</li>
                <li>• Payments processed securely via Stripe</li>
                <li>• Refunds available within 14 days</li>
              </ul>

              <h2 className="text-2xl font-bold mt-8 mb-4">6. Intellectual Property</h2>
              <p className="text-gray-300 mb-4">
                ClannAI retains all rights to our software, algorithms, and analysis methods. 
                You retain ownership of your uploaded footage and generated insights.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">7. Limitation of Liability</h2>
              <p className="text-gray-300 mb-4">
                ClannAI shall not be liable for any indirect, incidental, special, consequential, 
                or punitive damages resulting from your use of our services.
              </p>

              <h2 className="text-2xl font-bold mt-8 mb-4">8. Contact Us</h2>
              <p className="text-gray-300 mb-4">
                For questions about these Terms of Service, contact us at:
                <br />
                <span className="font-medium">legal@clann.ai</span>
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