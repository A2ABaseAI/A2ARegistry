# A2A Agent Registry UI

Modern Next.js single-page application for the A2A Agent Registry.

## Features

- 🚀 **Modern UI** - Built with Next.js 14, React 18, and Tailwind CSS
- 🔍 **Agent Search** - Real-time search with filtering
- 📱 **Responsive Design** - Works on all devices
- 🌙 **Dark Mode** - Automatic dark mode support
- 🔐 **Authentication** - User login and registration
- 📊 **Agent Discovery** - Browse and explore agents
- 💻 **Agent Details** - View full agent cards and capabilities

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- A2A Registry backend running (default: http://localhost:8000)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create `.env.local` file:

```bash
cp .env.example .env.local
```

3. Update the API URL in `.env.local` if needed:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:

```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
ui/
├── app/                    # Next.js app directory
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── login/              # Login page
│   ├── register/           # Registration page
│   └── agents/[id]/        # Agent detail page
├── components/             # React components
│   ├── Navbar.tsx          # Navigation bar
│   ├── SearchBar.tsx       # Search component
│   ├── AgentCard.tsx       # Agent card component
│   └── AgentList.tsx       # Agent list component
├── lib/                    # Utilities and API client
│   ├── api.ts              # API client with axios
│   └── utils.ts            # Utility functions
└── public/                 # Static assets
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The UI connects to the A2A Registry backend API. The API client is configured in `lib/api.ts` and includes:

- Agent endpoints (list, search, get, publish)
- Authentication endpoints (login, register, refresh)
- Health check endpoints

## Features in Detail

### Agent Discovery
- Browse public agents
- Real-time search with filtering
- View agent details and capabilities
- Responsive grid layout

### Authentication
- User registration
- Login with email/username
- Token-based authentication
- Protected routes (coming soon)

### Agent Details
- Full agent card view
- Skills and capabilities display
- JSON card viewer
- Responsive detail page

## Technology Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Pages

1. Create a new directory in `app/`
2. Add `page.tsx` file
3. Export default React component

### Adding New Components

1. Create component in `components/`
2. Use TypeScript for type safety
3. Follow Tailwind CSS styling patterns

### API Client

The API client (`lib/api.ts`) handles:
- Request/response interceptors
- Authentication token management
- Error handling
- Type definitions

## Production Build

```bash
npm run build
npm run start
```

## License

Same as the A2A Agent Registry project.

