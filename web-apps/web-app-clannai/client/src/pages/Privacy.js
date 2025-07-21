import React from 'react';

function Privacy() {
    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>

                <div className="prose prose-invert">
                    <h2>1. Data Collection</h2>
                    <p>Under UK GDPR Article 13, we collect:</p>
                    <ul>
                        <li>Game footage for analysis purposes</li>
                        <li>Team member information</li>
                        <li>Performance metrics and analysis results</li>
                    </ul>

                    <h2>2. Legal Basis</h2>
                    <p>We process data based on:</p>
                    <ul>
                        <li>Consent from all individuals in game footage</li>
                        <li>Legitimate interests for team performance analysis</li>
                        <li>Contractual necessity for service provision</li>
                    </ul>

                    <h2>3. Your Rights</h2>
                    <p>Under UK GDPR, you have the right to:</p>
                    <ul>
                        <li>Access your data</li>
                        <li>Request data deletion</li>
                        <li>Object to processing</li>
                        <li>Data portability</li>
                    </ul>

                    <h2>4. Contact Information</h2>
                    <p>Data Protection Officer: [Your Contact Info]</p>
                    <p>ICO Registration Number: [Your Number]</p>
                </div>
            </div>
        </div>
    );
}

export default Privacy; 