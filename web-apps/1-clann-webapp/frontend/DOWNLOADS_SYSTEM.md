# Downloads System - Interactive Video Preview & Export

## 🎯 Vision
Transform the Downloads tab into a professional video editing interface where users can preview exactly what they'll download and interactively adjust clip boundaries.

## 🏗️ Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GAME PAGE                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────────────┐   │
│  │   VIDEO PLAYER  │  │           UNIFIED SIDEBAR           │   │
│  │                 │  │  ┌─────┬─────┬─────┬─────────────┐  │   │
│  │  ┌───────────┐  │  │  │Events│Coach│Stats│ Downloads  │  │   │
│  │  │           │  │  │  └─────┴─────┴─────┴─────────────┘  │   │
│  │  │   Video   │  │  │                                     │   │
│  │  │           │  │  │  Downloads Tab:                     │   │
│  │  └───────────┘  │  │  ┌─────────────────────────────┐   │   │
│  │  Timeline       │  │  │ ☑️ Event 1 (2:30) Goal      │   │   │
│  │  ████▓▓░░░░░░░  │  │  │ ☑️ Event 2 (15:45) Shot     │   │   │
│  │                 │  │  │ ☐ Event 3 (23:10) Foul     │   │   │
│  └─────────────────┘  │  └─────────────────────────────┘   │   │
│                       │                                     │   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎬 Downloads Preview System

### Phase 1: Auto-Jump Preview (Current Goal)
```
User Flow:
1. Select events in Downloads tab
2. Click play button
3. Video auto-jumps between selected segments only

Timeline Behavior:
|----[====CLIP1====]------[===CLIP2===]----[====CLIP3====]----|
     2:25-2:35           15:40-15:50       23:05-23:15
     
Play Sequence:
Play → Jump to 2:25 → Play 10s → Jump to 15:40 → Play 10s → Jump to 23:05 → Play 10s → End
```

### Phase 2: Interactive Timeline Editor (Future Vision)
```
Advanced Timeline with Draggable Markers:

|----[====CLIP1====]------[===CLIP2===]----[====CLIP3====]----|
     ↑  ↑              ↑  ↑           ↑  ↑
  drag  drag        drag drag       drag drag
  start end         start end      start end

Features:
- Drag markers to adjust clip length
- Real-time duration display
- Visual feedback during drag
- Snap to event timestamps
- Gap detection and merging
```

## 🔧 Technical Implementation

### Current State Management
```typescript
// In UnifiedSidebar.tsx
const [selectedEvents, setSelectedEvents] = useState<Set<string>>(new Set())
const [activeTab, setActiveTab] = useState<'events' | 'coach' | 'stats' | 'downloads'>('events')

// In VideoPlayer.tsx  
const [currentTime, setCurrentTime] = useState(0)
const [isPlaying, setIsPlaying] = useState(false)
```

### Phase 1: Preview Mode Implementation
```typescript
// New states needed in VideoPlayer.tsx
const [isPreviewMode, setIsPreviewMode] = useState(false)
const [previewSegments, setPreviewSegments] = useState<PreviewSegment[]>([])
const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0)
const [segmentPadding, setSegmentPadding] = useState(5) // ±5 seconds

interface PreviewSegment {
  id: string
  start: number
  end: number
  event: GameEvent
}

// Segment calculation
const calculatePreviewSegments = (selectedEvents: Set<string>, events: GameEvent[], padding: number): PreviewSegment[] => {
  return Array.from(selectedEvents)
    .map(eventId => events.find(e => e.id === eventId))
    .filter(Boolean)
    .map(event => ({
      id: event.id,
      start: Math.max(0, event.timestamp - padding),
      end: event.timestamp + padding,
      event
    }))
    .sort((a, b) => a.start - b.start)
}

// Auto-jump logic
const handleTimeUpdate = () => {
  if (!isPreviewMode || previewSegments.length === 0) return
  
  const currentSegment = previewSegments[currentSegmentIndex]
  if (currentTime >= currentSegment.end) {
    jumpToNextSegment()
  }
}

const jumpToNextSegment = () => {
  const nextIndex = currentSegmentIndex + 1
  if (nextIndex < previewSegments.length) {
    setCurrentSegmentIndex(nextIndex)
    videoRef.current.currentTime = previewSegments[nextIndex].start
  } else {
    // End of preview
    setIsPlaying(false)
    setCurrentSegmentIndex(0)
  }
}
```

## 📁 File Structure
```
frontend/src/
├── app/games/[id]/
│   └── page.tsx                 # Main game page, manages selectedEvents
├── components/games/
│   ├── VideoPlayer.tsx          # Video playback + preview logic
│   └── UnifiedSidebar.tsx       # Downloads tab + event selection
└── lib/
    └── types.ts                 # GameEvent, PreviewSegment interfaces
```

## 🎮 User Experience Flow

### Current Downloads Tab
```
1. User clicks Downloads tab
2. Sees list of events with checkboxes
3. Selects events (max 10)
4. Clicks "Create Highlights" button
5. Downloads combined video file
```

### Enhanced Preview Flow
```
1. User clicks Downloads tab
2. Selects events (whole card clickable)
3. Video player enters "Preview Mode"
4. Timeline shows selected segments highlighted
5. Play button only plays selected segments
6. User can adjust ±padding with slider
7. Real-time preview of final output
8. Download button creates exact preview
```

## 🚀 Implementation Phases

### ✅ Phase 0: Foundation (Complete)
- [x] Event selection in Downloads tab
- [x] Clickable event cards
- [x] Remove 5-event limit (now 10)
- [x] Bin button functionality

### 🔄 Phase 1: Auto-Jump Preview (In Progress)
- [ ] Detect Downloads tab active state
- [ ] Calculate preview segments from selected events
- [ ] Implement auto-jump video logic
- [ ] Add segment padding control (±5s slider)
- [ ] Visual feedback on timeline

### 🔮 Phase 2: Interactive Timeline Editor (Future)
- [ ] Draggable segment markers
- [ ] Real-time clip duration display
- [ ] Segment overlap detection/merging
- [ ] Frame-level precision controls
- [ ] Export format presets

### 🎨 Phase 3: Professional Features (Future)
- [ ] Transition effects between clips
- [ ] Audio fade in/out
- [ ] Custom overlay graphics
- [ ] Multiple export formats
- [ ] Batch processing

## 🎯 Success Metrics
- **User Engagement**: Time spent in Downloads tab
- **Preview Usage**: % of downloads that use preview first
- **Clip Quality**: User satisfaction with final exports
- **Professional Adoption**: Sports teams using advanced features

## 💡 Competitive Advantage
> "Most sports analysis tools give you basic clips. This is a full video production suite built into match analysis."

### Key Differentiators:
1. **Real-time Preview**: See exactly what you'll download
2. **Interactive Editing**: Drag to adjust clip boundaries
3. **Professional Output**: Frame-perfect highlights
4. **Integrated Workflow**: Analysis → Selection → Editing → Export

---

*This system transforms ClannAI from a match analysis tool into a complete video production platform for sports content creators.*