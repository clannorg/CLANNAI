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

### Phase 1: Smart Timeline Preview (Current Goal)
```
User Flow:
1. Select events in Clips tab
2. Timeline shows full match with visual distinction
3. Play button only plays selected segments

Smart Timeline Design:
|----[====CLIP1====]------[===CLIP2===]----[====CLIP3====]----|
grey   GREEN/BRIGHT      grey  GREEN      grey  GREEN      grey

Visual System:
- GREY = Rest of match (visible but dimmed)
- GREEN = Selected clips (bright/highlighted) 
- Same timeline length (full match duration)
- Same scrubbing ability (click anywhere)
- Smart playback (only plays green segments)

Play Sequence:
Play → Jump to first GREEN → Play segment → Skip GREY → Jump to next GREEN → Repeat
User can scrub to grey areas but auto-play only affects green segments
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

### Phase 1: Smart Timeline Implementation
```typescript
// New states needed in VideoPlayer.tsx
const [isClipsMode, setIsClipsMode] = useState(false)
const [clipSegments, setClipSegments] = useState<ClipSegment[]>([])
const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0)
const [segmentPadding, setSegmentPadding] = useState(5) // ±5 seconds

interface ClipSegment {
  id: number
  start: number
  end: number
  event: GameEvent
}

// Smart timeline styling
const generateTimelineBackground = (segments: ClipSegment[], duration: number) => {
  if (segments.length === 0) return 'rgba(255,255,255,0.3)' // Default grey
  
  let gradientStops = []
  let lastEnd = 0
  
  segments.forEach((segment, index) => {
    const startPercent = (segment.start / duration) * 100
    const endPercent = (segment.end / duration) * 100
    
    // Grey section before clip
    if (startPercent > lastEnd) {
      gradientStops.push(`rgba(255,255,255,0.2) ${lastEnd}%`)
      gradientStops.push(`rgba(255,255,255,0.2) ${startPercent}%`)
    }
    
    // Green clip section
    gradientStops.push(`#22C55E ${startPercent}%`)
    gradientStops.push(`#22C55E ${endPercent}%`)
    
    lastEnd = endPercent
  })
  
  // Grey section after last clip
  if (lastEnd < 100) {
    gradientStops.push(`rgba(255,255,255,0.2) ${lastEnd}%`)
    gradientStops.push(`rgba(255,255,255,0.2) 100%`)
  }
  
  return `linear-gradient(to right, ${gradientStops.join(', ')})`
}

// Smart play logic
const handleTimeUpdate = () => {
  // ... existing logic ...
  
  // Clips mode auto-jump logic
  if (isClipsMode && clipSegments.length > 0 && isPlaying) {
    const currentSegment = clipSegments[currentSegmentIndex]
    
    // Hit end of green segment? Jump to next green segment
    if (currentSegment && time >= currentSegment.end) {
      jumpToNextClipSegment()
    }
    
    // In grey area while playing? Jump to next green segment
    const inGreenSegment = clipSegments.some(seg => time >= seg.start && time <= seg.end)
    if (!inGreenSegment) {
      jumpToNextClipSegment()
    }
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

### Enhanced Clips Flow
```
1. User clicks Clips tab
2. Selects events (whole card clickable)
3. Timeline transforms with smart styling:
   - Full match timeline (same length)
   - Selected clips = bright green
   - Rest of match = dimmed grey
4. Play button enters "Smart Preview Mode":
   - Only plays green segments
   - Auto-skips grey areas
   - User can still scrub anywhere
5. User can adjust ±padding with slider
6. Real-time preview of final output
7. Download button creates exact preview
```

## 🚀 Implementation Phases

### ✅ Phase 0: Foundation (Complete)
- [x] Event selection in Downloads tab
- [x] Clickable event cards
- [x] Remove 5-event limit (now 10)
- [x] Bin button functionality

### 🔄 Phase 1: Smart Timeline Preview (In Progress)
- [x] Detect Clips tab active state
- [x] Calculate clip segments from selected events  
- [x] Basic auto-jump video logic (needs refinement)
- [ ] Smart timeline styling (green/grey gradient)
- [ ] Enhanced play logic (skip grey areas)
- [ ] Add segment padding control (±5s slider)
- [ ] Visual feedback and polish

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
1. **Smart Timeline Preview**: Visual distinction between clips and full match
2. **Intelligent Playback**: Only plays selected segments, skips irrelevant parts
3. **Familiar Interface**: Same timeline/controls, just enhanced behavior
4. **Real-time Preview**: See exactly what you'll download
5. **Interactive Editing**: Drag to adjust clip boundaries (Phase 2)
6. **Professional Output**: Frame-perfect highlights
7. **Integrated Workflow**: Analysis → Selection → Preview → Export

### The "GOAT Selling Point":
**Smart Timeline System** - Users get professional video editing capabilities without learning new interfaces. Same familiar video player, but with intelligent preview that shows exactly what they're creating.

---

*This system transforms ClannAI from a match analysis tool into a complete video production platform for sports content creators.*