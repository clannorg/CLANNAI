import React from 'react';

function Terms() {
    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold mb-6">Terms & Conditions</h1>

                <div className="prose prose-invert">
                    <h2>1. Agreement to Terms</h2>
                    <p>By accessing or using Clann AI, you agree to be bound by these terms, which are governed by Northern Ireland law.</p>

                    <h2>2. Video Upload Rights</h2>
                    <ul>
                        <li>You must have explicit permission to upload game footage</li>
                        <li>All individuals in the footage must have consented to AI analysis</li>
                        <li>You must comply with UK GDPR requirements for data sharing</li>
                    </ul>

                    <h2>3. Data Processing</h2>
                    <ul>
                        <li>Game footage is processed within the European Economic Area</li>
                        <li>Analysis results are stored securely on AWS servers</li>
                        <li>Data is retained according to our retention policy</li>
                    </ul>

                    <h2>4. User Responsibilities</h2>
                    <ul>
                        <li>Maintain confidentiality of team access codes</li>
                        <li>Use analysis data in accordance with data protection laws</li>
                        <li>Report any unauthorized access immediately</li>
                    </ul>

                    <h2>5. Dispute Resolution</h2>
                    <p>Any disputes will be resolved under Northern Ireland jurisdiction.</p>
                </div>
            </div>
        </div>
    );
}

export default Terms; 