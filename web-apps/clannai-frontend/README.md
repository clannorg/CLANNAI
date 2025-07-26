# ClannAI Frontend (Next.js)

## 🚀 Overview

This is the **Next.js + TypeScript** frontend for the ClannAI platform. It provides a modern, scalable, and maintainable web interface for football video analysis, team management, and event annotation. The app is designed for rapid development, robust user experience, and seamless integration with backend APIs and video processing services.

---

## 🏗️ Project Structure

```
clannai-frontend/
├── public/                  # Static assets (images, videos, favicon, etc.)
├── src/
│   ├── pages/               # Next.js pages (routing)
│   ├── components/          # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   ├── context/             # React context providers
│   ├── lib/                 # Utility functions, API clients
│   ├── styles/              # Tailwind/global CSS
│   ├── types/               # TypeScript types/interfaces
│   └── ...                  # Other feature folders
├── video-player-package/    # Modular, reusable video player component
├── events/                  # Event schemas, logic, and utilities
├── tsconfig.json            # TypeScript configuration
├── next.config.ts           # Next.js configuration
├── postcss.config.mjs       # PostCSS/Tailwind config
├── package.json             # Project dependencies and scripts
└── ...                      # Other configs and docs
```

---

## ✨ Key Features

- **Next.js 15+**: File-based routing, SSR/SSG, API routes
- **TypeScript**: Type safety across the codebase
- **Tailwind CSS**: Utility-first styling
- **Reusable Video Player**: Modular package for HLS/MP4 playback, event overlays
- **Event Management**: Create, edit, and filter game events
- **Authentication**: Modal-based login/register (NextAuth.js or custom)
- **Team & Game Management**: Dashboard for teams, games, uploads
- **Responsive Design**: Works on desktop, tablet, and mobile
- **API Integration**: Connects to backend for auth, data, uploads

---

## ⚡️ Getting Started

### 1. **Install Dependencies**
```bash
npm install
```

### 2. **Run the Development Server**
```bash
npm run dev
```
Visit [http://localhost:3000](http://localhost:3000) to view the app.

### 3. **Environment Variables**
- Copy `.env.example` to `.env.local` and fill in required values (API URLs, keys, etc.).
- All secrets should be managed via environment variables, not committed to git.

### 4. **Build for Production**
```bash
npm run build
npm start
```

---

## 🧩 Main Folders & Conventions

- **`/src/pages`**: Each file = a route. Use nested folders for dashboard, game, settings, etc.
- **`/src/components`**: All UI elements (modals, forms, video player, timeline, etc.)
- **`/video-player-package`**: Standalone, reusable video player (imported where needed)
- **`/events`**: Event schemas, types, and logic for tagging/annotation
- **`/public`**: Static files (images, videos, etc.)
- **`/src/hooks`**: Custom React hooks for API, auth, state, etc.
- **`/src/context`**: React context providers (auth, team, etc.)
- **`/src/types`**: TypeScript types/interfaces for API, models, etc.

---

## 🛠️ Development Workflow

- **Feature branches:** Use `feature/your-feature` for new work.
- **Code style:** Enforced via ESLint and Prettier.
- **Type safety:** All new code should use TypeScript.
- **Pull requests:** Required for all merges to main.
- **Testing:** Add unit/integration tests for new features.

---

## 🌐 Deployment

- **Preview/Production:** Deploy to Vercel or your preferred Next.js host.
- **Environment variables:** Set via the host dashboard for each environment.
- **Static assets:** Served from `/public`.
- **API routes:** Use `/src/pages/api` for serverless functions if needed.

---

## 📚 Documentation & References

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Radix UI](https://www.radix-ui.com/) (if used)
- [React Query](https://tanstack.com/query/latest) (if used)

---

## 🧑‍💻 Contributing

1. Fork the repo and create your branch from `main`.
2. Make your changes and add tests as needed.
3. Run `npm run lint` and `npm run test` before pushing.
4. Open a pull request and describe your changes.

---

## 🛡️ Security & Secrets

- **Never commit secrets** (API keys, tokens, etc.) to the repo.
- Use environment variables for all sensitive config.
- Review `.gitignore` to ensure no secrets are tracked.

---

## 🏁 License

MIT License. See [LICENSE](./LICENSE) for details. 