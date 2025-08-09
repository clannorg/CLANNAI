# Mobile Video Player Layout Plan

## Overview
Transform the game video view to work like YouTube mobile - adaptive layout based on device orientation.

## Current State (Desktop/Landscape)
```
┌─────────────────────────────────────────────────────────────┐
│ GameHeader (scores, title, controls)                       │
├─────────────────────────────────┬───────────────────────────┤
│                                 │ ┌─ Events ─ AI ─ Insights │
│                                 │ │                         │
│         VideoPlayer             │ │   UnifiedSidebar        │
│      (with timeline +           │ │   (floating right)      │
│       rich controls)            │ │                         │
│                                 │ │   - Events list         │
│                                 │ │   - AI Chat             │
│                                 │ │   - Insights            │
│                                 │ │   - Downloads           │
│                                 │ │                         │
└─────────────────────────────────┴─┴─────────────────────────┘
```
**Status:** ✅ Works fine on desktop/laptop

## Target Mobile Layout

### Portrait Mode (New YouTube-style)
```
┌─────────────────────────────────┐
│ ┌─ GameHeader (overlay) ───────┐ │
│ │ greenisland vs Olympic       │ │
│ │ 0-0        📱 AI Coach       │ │
│ └─────────────────────────────┘ │
│                                 │
│         VideoPlayer             │
│      (simplified controls)      │
│       aspect-video sizing       │
│                                 │
├─────────────────────────────────┤
│ [Events][AI Coach][Insights][⬇] │ ← Sticky tabs
├─────────────────────────────────┤
│                                 │
│     Tab Content Area            │
│   (Events list, AI chat, etc.)  │
│                                 │
│     ↕ Scrollable content        │
│                                 │
│                                 │
└─────────────────────────────────┘
```

### Landscape Mode (Keep current)
```
┌─────────────────────────────────────────────────────────────┐
│ GameHeader                                                  │
├─────────────────────────────────┬───────────────────────────┤
│                                 │ ┌─ Events ─ AI ─ Insights │
│         VideoPlayer             │ │   UnifiedSidebar        │
│      (full rich controls)       │ │   (floating right)      │
│                                 │ │                         │
└─────────────────────────────────┴─┴─────────────────────────┘
```

## Code Structure Changes

### 1. New Hook: `useOrientation()`
```typescript
// hooks/useOrientation.ts
const useOrientation = () => {
  const [isPortrait, setIsPortrait] = useState(false)
  // Detect orientation changes
  return { isPortrait, isLandscape: !isPortrait }
}
```

### 2. Updated Game Page (`games/[id]/page.tsx`)
```typescript
const { isPortrait } = useOrientation()

return (
  <div className="min-h-screen bg-black">
    {isPortrait ? (
      // Mobile Portrait Layout
      <MobilePortraitLayout />
    ) : (
      // Desktop/Landscape Layout (current)
      <DesktopLayout />
    )}
  </div>
)
```

### 3. Component Adaptations

#### VideoPlayer.tsx
- **Portrait:** Simplified controls, larger touch targets
- **Landscape:** Keep current rich controls
- **Both:** Same core video functionality

#### UnifiedSidebar.tsx  
- **Portrait:** Render as bottom content (not floating)
- **Landscape:** Keep current floating sidebar behavior
- **Both:** Same tab content and functionality

#### GameHeader.tsx
- **Portrait:** Overlay on video with gradient background
- **Landscape:** Keep current header positioning

## Implementation Steps

### Phase 1: Foundation
1. ✅ Create `useOrientation()` hook
2. ✅ Add orientation detection to game page
3. ✅ Create basic portrait/landscape layout split

### Phase 2: Mobile Layout
1. ✅ Implement YouTube-style portrait layout
2. ✅ Move sidebar content to bottom tabs
3. ✅ Adapt video controls for mobile

### Phase 3: Responsive Polish
1. ✅ Optimize touch targets and spacing
2. ✅ Test orientation changes
3. ✅ Fine-tune mobile experience

## File Changes

### New Files
- `hooks/useOrientation.ts` - Orientation detection
- `MOBILE_VIDEO_LAYOUT_PLAN.md` - This plan

### Modified Files
- `games/[id]/page.tsx` - Layout orchestration
- `components/games/VideoPlayer.tsx` - Mobile controls
- `components/games/UnifiedSidebar.tsx` - Bottom layout mode
- `components/games/GameHeader.tsx` - Overlay mode

## Key Benefits

✅ **Desktop unchanged** - Current experience preserved
✅ **Mobile portrait fixed** - YouTube-like experience  
✅ **Mobile landscape works** - Uses current desktop layout
✅ **Same functionality** - All features work in both modes
✅ **Touch-friendly** - Proper mobile interaction

## Final Result

**Desktop/Laptop users:** Same great experience
**Mobile users:** Professional YouTube-style video experience
**All users:** Seamless orientation switching