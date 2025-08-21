# Timeline Controls Redesign Plan

## Current Layout Issues
- Play button cramped with time display
- Skip buttons too close to play
- Timeline progress bar squeezed
- Poor visual hierarchy

## New Layout Vision - YouTube Mobile Style

### Two-Row Layout:

**Row 1 - Main Controls (Centered):**
```
[◀ Prev Event]    [-5s]    [▶️ PLAY]    [+5s]    [Next Event ▶]
```

**Row 2 - Timeline & Time:**
```
[5:07] [████████████████████████████████████] [52:06] [🔊]
```

### Spacing & Positioning:
- **Play Button**: Large, dead center of top row
- **Skip Buttons**: ±5s buttons immediately flanking play button
- **Event Navigation**: Previous/Next event buttons at outer edges of top row
- **Timeline Bar**: Full width on bottom row between time displays
- **Time Display**: Current time (left), Duration (right) on bottom row
- **Volume**: Far right on bottom row

### Visual Hierarchy:
1. **Primary**: Large centered play button (top row)
2. **Secondary**: ±5s skip buttons (top row, flanking play)
3. **Tertiary**: Event navigation (top row, outer edges)
4. **Info**: Timeline and time displays (bottom row)

## ASCII Layout Diagram:
```
┌─────────────────────────────────────────────────────────────────────────┐
│              [◀]    [-5s]    [▶️ PLAY]    [+5s]    [▶]                  │
│                                                                         │
│  5:07  ████████████████████████████████████████████████  52:06  [🔊]   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Implementation Notes:
- Play button should be visually prominent (larger size)
- Consistent spacing between related controls
- Timeline bar gets flex-1 to fill remaining space
- Responsive design maintains hierarchy on smaller screens

## Benefits:
- Clear visual focus on primary play control
- Logical grouping of related functions
- Better use of available space
- Improved user experience and accessibility