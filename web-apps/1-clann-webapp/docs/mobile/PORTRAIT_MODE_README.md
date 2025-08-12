## Mobile Portrait Mode — 1-clann-webapp

Short guide to how the YouTube-style portrait layout works and where to tweak it.

### What users see
- Video at the top; Events / AI Coach / Insights / Downloads bar directly below.
- Only the tab content scrolls. Video and the tab bar stay pinned.
- Tapping the video shows overlays (header, timeline, controls), then everything fades after 4s back to a clean video.

### Key files
- `frontend/src/app/games/[id]/page.tsx`
  - Chooses portrait vs landscape using `useOrientation()`.
  - Renders `UnifiedSidebar` in mobile mode and passes `mobileVideoComponent`.
  - `MobileVideoPlayer` manages the 4s auto-hide and tap-to-toggle behavior.

- `frontend/src/components/games/VideoPlayer.tsx`
  - Accepts `overlayVisible` and `onUserInteract`.
  - Timeline dots, scrub bar, and controls are one overlay block that fades with `overlayVisible`.

- `frontend/src/components/games/GameHeader.tsx`
  - The small gradient header shown over the video in portrait. It follows the same show/hide state as the overlays.

- `frontend/src/components/games/UnifiedSidebar.tsx`
  - In mobile mode, uses a sticky video header area and a sticky tab header.
  - The tab header is positioned with `top-[56.25vw]` so it sits directly under a 16:9 video.

### How portrait mode is decided
- `useOrientation()` exposes `isPortrait` / `isLandscape`.
- In `page.tsx`, if `isLandscape` → desktop layout; else → mobile portrait layout.

### Overlay auto‑hide (4s)
- `MobileVideoPlayer` in `page.tsx` owns `showOverlay` state.
- On any interaction (tap, mouse move, key), it resets a timer to 4,000 ms and sets `showOverlay = true`.
- After 4s of inactivity, `showOverlay = false`.
- `VideoPlayer` receives `overlayVisible={showOverlay}` and fades its entire overlay block (timeline dots + scrub + controls).

### Sticky elements on mobile
- Video area (via `mobileVideoComponent` in `UnifiedSidebar`) is sticky at the top.
- Tab header (Events / AI Coach / Insights / Downloads) is sticky with `top-[56.25vw]` so it aligns beneath the video.
- The list content under the tabs scrolls independently.

### Config knobs
- Auto‑hide duration: change `4000` in `MobileVideoPlayer` (in `page.tsx`).
- Sticky offset for tab header: `top-[56.25vw]` in `UnifiedSidebar.tsx`.
  - 56.25vw assumes a 16:9 video (`9/16 = 0.5625`). If the aspect ratio changes, update this value accordingly.

### Acceptance checklist
- Portrait: tapping the video shows header + timeline + controls; after 4s they fade out.
- Portrait: scrolling keeps the video and the tab header pinned; only tab content scrolls.
- Landscape/desktop: existing layout unchanged.

### Notes / limitations
- iOS Safari’s URL bar can affect viewport height; using vw for sticky offsets is deliberate for stability.
- If the video aspect ratio is changed globally, remember to update the sticky offset.

### Recently touched files (portrait work)
- `frontend/src/app/games/[id]/page.tsx`
- `frontend/src/components/games/VideoPlayer.tsx`
- `frontend/src/components/games/UnifiedSidebar.tsx`

