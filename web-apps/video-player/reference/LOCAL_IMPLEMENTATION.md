# Local Video Player Implementation Guide

## Quick Start

### 1. Create New Next.js App
```bash
npx create-next-app@latest local-video-player --typescript --tailwind --eslint
cd local-video-player
```

### 2. Install Dependencies
```bash
npm install lucide-react sonner
```

### 3. Copy Components
Copy all files from `video-player-reference/components/` to your new app's `src/components/video-player/`

### 4. Copy Hooks
Copy all files from `video-player-reference/hooks/` to your new app's `src/hooks/`

### 5. Copy UI Components
Copy all files from `video-player-reference/ui-components/` to your new app's `src/components/ui/`

## Key Modifications Needed

### 1. Replace API Calls with Local File Handling

**Original (API-based):**
```typescript
const { data: videos = [] } = useGameVideos(gameId)
```

**Local Implementation:**
```typescript
const [selectedVideo, setSelectedVideo] = useState<File | null>(null)
const [videoUrl, setVideoUrl] = useState<string>('')

const handleFileSelect = (file: File) => {
  const url = URL.createObjectURL(file)
  setSelectedVideo(file)
  setVideoUrl(url)
}
```

### 2. Add File Input Component

```typescript
function FileInput({ onFileSelect }: { onFileSelect: (file: File) => void }) {
  return (
    <div className="p-8 border-2 border-dashed border-gray-300 rounded-lg text-center">
      <input
        type="file"
        accept="video/*"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) onFileSelect(file)
        }}
        className="hidden"
        id="video-input"
      />
      <label htmlFor="video-input" className="cursor-pointer">
        <div className="text-gray-600">
          <Upload className="h-12 w-12 mx-auto mb-4" />
          <p>Click to select a video file</p>
          <p className="text-sm">Supports MP4, WebM, and other formats</p>
        </div>
      </label>
    </div>
  )
}
```

### 3. Main Page Implementation

```typescript
export default function Home() {
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [videoUrl, setVideoUrl] = useState<string>('')

  const handleFileSelect = (file: File) => {
    const url = URL.createObjectURL(file)
    setVideoFile(file)
    setVideoUrl(url)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {!videoFile ? (
        <div className="flex items-center justify-center min-h-screen">
          <FileInput onFileSelect={handleFileSelect} />
        </div>
      ) : (
        <VideoPlayerWithEvents
          videoUrl={videoUrl}
          videoFile={videoFile}
          showGameScoreBanner={true}
          showVideoTimeline={true}
          showVideoControls={true}
          showEventsManager={true}
        />
      )}
    </div>
  )
}
```

### 4. Modify VideoPlayerWithEvents

Update the component to accept local video props instead of API-based props:

```typescript
interface LocalVideoPlayerProps {
  videoUrl: string
  videoFile: File
  showGameScoreBanner?: boolean
  showVideoTimeline?: boolean
  showVideoControls?: boolean
  showEventsManager?: boolean
}
```

### 5. Local Event Storage

Replace API event storage with localStorage:

```typescript
// Save events to localStorage
const saveEvents = (events: Event[]) => {
  localStorage.setItem('video-events', JSON.stringify(events))
}

// Load events from localStorage
const loadEvents = (): Event[] => {
  const stored = localStorage.getItem('video-events')
  return stored ? JSON.parse(stored) : []
}
```

## Key Features to Implement

1. **File Selection** - HTML5 file input for video selection
2. **Local Video Playback** - Use object URLs for local files
3. **Event Persistence** - Store events in localStorage
4. **Same UI/UX** - Keep all the existing components and styling
5. **No Backend** - Everything runs locally

## Testing

1. **Test with different video formats** (MP4, WebM, etc.)
2. **Test event tagging** - Create, edit, delete events
3. **Test sidebar toggle** - Show/hide events panel
4. **Test fullscreen mode** - Video should go fullscreen
5. **Test timeline interaction** - Click to seek, event markers

## Notes

- Remove all API client dependencies
- Replace authentication with simple local state
- Keep all the event validation and auto-generation logic
- Maintain the same visual design and user experience 