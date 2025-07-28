export default function Privacy() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-16">
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
  )
} 