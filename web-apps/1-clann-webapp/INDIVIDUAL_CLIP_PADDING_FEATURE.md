# Individual Clip Padding Feature

## 🎯 Overview
Allow users to set custom "before" and "after" padding for each individual selected event when creating highlight reels, replacing the current global padding system.

## 🎨 UI Design
```
┌─────────────────────────────────────────────────────────────┐
│ 🎬 Create Highlights                                        │
│ Select events to create a highlight reel for social media  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ● Goal 6:27                                            [🗑] │
│   A right-footed shot from just outside the penalty...     │
│   ⏪ Before: ├──●────┤ 3s    ⏩ After: ├────●──┤ 5s        │
│                                                             │
│ ● Goal 6:53                                            [🗑] │
│   A player in a white shirt shoots from distance...        │
│   ⏪ Before: ├────●──┤ 5s    ⏩ After: ├──●────┤ 3s        │
│                                                             │
│ ● Goal 8:49                                            [🗑] │
│   A powerful shot hits the top bar of the goal...          │
│   ⏪ Before: ├──────●┤ 8s    ⏩ After: ├●──────┤ 1s        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Selected Events:                                    3 / 10  │
│ Total Duration:                        25s (3+6+8+1+8+1)   │
│                                                             │
│ [Create Highlight Reel]                                    │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Technical Implementation

### Data Structure Change
**Current:**
```typescript
// Global padding for all events
const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set())
const [clipPadding, setClipPadding] = useState(5) // seconds
```

**New:**
```typescript
// Individual padding per event
const [selectedEvents, setSelectedEvents] = useState<Map<number, {
  beforePadding: number,  // 0-15 seconds before event
  afterPadding: number    // 0-15 seconds after event
}>>(new Map())
```

### Component Updates Required

#### 1. `page.tsx` (Main Game Page)
- **Change state structure** from `Set<number>` to `Map<number, PaddingData>`
- **Update event selection logic** to initialize with default padding
- **Pass Map to child components** instead of Set + global padding

#### 2. `UnifiedSidebar.tsx` (Downloads Tab)
- **Render 2 sliders per selected event** (before/after)
- **Update duration calculation** to sum individual paddings
- **Handle padding updates** for specific events
- **Remove global padding slider**

#### 3. `VideoPlayer.tsx` (Preview Logic)
- **Use individual padding values** for segment calculation
- **Update preview segments** based on per-event padding
- **Handle Map structure** instead of Set + global padding

### Key Functions

```typescript
// Add event with default padding
const addEvent = (eventId: number) => {
  setSelectedEvents(prev => new Map(prev).set(eventId, {
    beforePadding: 5,  // default 5s before
    afterPadding: 5    // default 5s after
  }))
}

// Remove event
const removeEvent = (eventId: number) => {
  setSelectedEvents(prev => {
    const newMap = new Map(prev)
    newMap.delete(eventId)
    return newMap
  })
}

// Update specific padding
const updateEventPadding = (
  eventId: number, 
  type: 'before' | 'after', 
  value: number
) => {
  setSelectedEvents(prev => {
    const newMap = new Map(prev)
    const current = newMap.get(eventId) || { beforePadding: 5, afterPadding: 5 }
    newMap.set(eventId, {
      ...current,
      [type === 'before' ? 'beforePadding' : 'afterPadding']: value
    })
    return newMap
  })
}

// Calculate total duration
const calculateTotalDuration = (selectedEvents: Map<number, PaddingData>) => {
  let total = 0
  selectedEvents.forEach(({ beforePadding, afterPadding }) => {
    total += beforePadding + afterPadding
  })
  return total
}
```

### UI Components

#### Individual Event Padding Controls
```typescript
// For each selected event in UnifiedSidebar
<div className="mt-2 space-y-2">
  {/* Before Padding Slider */}
  <div className="flex items-center gap-3">
    <span className="text-xs text-gray-400 w-12">⏪ Before:</span>
    <input
      type="range"
      min="0"
      max="15"
      step="1"
      value={eventData.beforePadding}
      onChange={(e) => updateEventPadding(eventId, 'before', parseInt(e.target.value))}
      className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
    />
    <span className="text-xs text-orange-400 w-8">{eventData.beforePadding}s</span>
  </div>
  
  {/* After Padding Slider */}
  <div className="flex items-center gap-3">
    <span className="text-xs text-gray-400 w-12">⏩ After:</span>
    <input
      type="range"
      min="0"
      max="15"
      step="1"
      value={eventData.afterPadding}
      onChange={(e) => updateEventPadding(eventId, 'after', parseInt(e.target.value))}
      className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
    />
    <span className="text-xs text-orange-400 w-8">{eventData.afterPadding}s</span>
  </div>
</div>
```

## 🎯 User Experience

### Benefits
- **Precise control** over each clip's timing
- **Mix and match** padding (e.g., 8s before + 1s after)
- **Visual feedback** with live duration updates
- **Intuitive sliders** with clear before/after labels

### Default Behavior
- New events start with **5s before + 5s after** (current default)
- Users can adjust from **0-15s** on each side
- Total duration updates in real-time

### Edge Cases
- **0s padding**: Event plays exactly at timestamp
- **15s max**: Prevents excessively long clips
- **Event boundaries**: Padding respects video start/end times

## 🚀 Implementation Steps

1. **Update data structures** in `page.tsx`
2. **Modify event selection logic** to use Map
3. **Rebuild UnifiedSidebar** padding controls
4. **Update VideoPlayer** preview logic
5. **Test duration calculations**
6. **Polish UI styling** and transitions

## 📊 No Database Changes Required
This feature uses **session-only state** - no persistence needed between visits. Users select events, adjust padding, and download immediately.