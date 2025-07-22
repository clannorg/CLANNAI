import Link from 'next/link';

export default function Home() {
  const sessions = [
    {
      id: '1',
      name: 'Football Game Analysis',
      videoFile: 'Game298_0601_p1.mp4',
      eventsFile: 'footy.json',
      duration: '14:12',
      eventCount: 43,
      createdAt: '2024-01-15'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Football Analytics
          </h1>
          <p className="text-gray-600">
            View and analyze football game events
          </p>
        </div>

        {/* Sessions List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Sessions ({sessions.length})
            </h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {sessions.map((session) => (
              <div key={session.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {session.name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>📹 {session.videoFile}</span>
                      <span>⏱️ {session.duration}</span>
                      <span>📊 {session.eventCount} events</span>
                      <span>📅 {session.createdAt}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <Link 
                      href={`/session/${session.id}`}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Open Session
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Empty State (if no sessions) */}
        {sessions.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-9 0h10m-10 0a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V6a2 2 0 00-2-2" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No sessions yet
            </h3>
            <p className="text-gray-500 mb-4">
              Upload a video to get started with your first session.
            </p>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
              Upload Video
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
