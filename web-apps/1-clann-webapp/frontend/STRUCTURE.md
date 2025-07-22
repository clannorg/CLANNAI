# 📁 Simple Folder Structure

```
frontend/
├── public/
│   ├── clann-sliothar.png
│   ├── clann.ai-green.png
│   ├── clann.ai-white.png
│   └── favicon.ico
│
├── src/
│   ├── app/
│   │   ├── layout.tsx                  # Root layout
│   │   ├── page.tsx                    # Landing page
│   │   ├── globals.css                 # Global styles
│   │   │
│   │   ├── dashboard/
│   │   │   └── page.tsx                # Dashboard with Team/Games toggle
│   │   │
│   │   └── games/
│   │       └── [id]/
│   │           └── page.tsx            # Game detail with video player
│   │
│   ├── components/
│   │   ├── ui/                         # Button, Card, Input, etc.
│   │   ├── video-player/               # Video player component
│   │   ├── dashboard/                  # Dashboard components
│   │   └── landing/                    # Landing page components
│   │
│   ├── lib/
│   │   ├── utils.ts                    # Utility functions
│   │   └── constants.ts                # Colors, spacing, etc.
│   │
│   └── types/                          # TypeScript types
│
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## 🎯 **3 Main Pages**

- `/` - Landing page
- `/dashboard` - Dashboard with toggle
- `/games/[id]` - Game detail with video

## 🎨 **Simple & Clean**

No over-engineering, just what you need to get it working today. 