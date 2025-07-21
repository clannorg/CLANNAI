import React from 'react';

function SubscriptionManager({ teamStatus, user, setFeedback, handleTrialUpgrade, sessions }) {
  const handleBillingPortal = async () => {
    try {
      const currentTeam = sessions.find(s => s.team_name !== 'ClannAI demo');
      if (!currentTeam?.team_id) {
          throw new Error('No team selected');
      }

      console.log('Attempting portal URL:', `${process.env.REACT_APP_API_URL}/teams/${currentTeam.team_id}/billing-portal`);

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/teams/${currentTeam.team_id}/billing-portal`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to access billing portal');
      const { url } = await response.json();
      window.open(url, '_blank');
    } catch (err) {
      console.error('Billing portal error:', err);
      setFeedback({
        type: 'error',
        message: 'Failed to open billing portal'
      });
    }
  };

  return (
    <div className="mb-6 p-4 bg-gray-50 rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <p className="text-gray-900 font-medium">Current Plan</p>
        <span className={`px-2 py-1 rounded-full text-xs ${
          teamStatus.isPremium ? 'bg-green-400/10 text-green-400' : 'bg-gray-400/10 text-gray-400'
        }`}>
          {teamStatus.isPremium ? '⭐️ PREMIUM' : 'FREE TIER'}
        </span>
      </div>
      
      {teamStatus.isPremium ? (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Manage your subscription, update payment method, or view billing history
          </p>
          <button
            onClick={handleBillingPortal}
            className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg 
                     hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
          >
            <span>Manage Subscription</span>
            <span className="text-xs">↗</span>
          </button>
        </>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Upgrade to Premium for unlimited matches and advanced analytics
          </p>
          <button
            onClick={handleTrialUpgrade}
            className="w-full px-4 py-2 bg-green-50 text-green-700 rounded-lg 
                     hover:bg-green-100 transition-colors"
          >
            Upgrade to Premium
          </button>
        </>
      )}
    </div>
  );
}

export default SubscriptionManager; 