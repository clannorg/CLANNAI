export default function Terms() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-16">
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
  )
} 