# A2A Registry Frontend Development Guide

This guide provides comprehensive information for developers working on the A2A Agent Registry frontend.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Basic knowledge of React, TypeScript, and Tailwind CSS

### Installation
```bash
cd frontend
npm install --legacy-peer-deps
```

### Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── __tests__/      # Component tests
│   ├── Button.tsx      # Button component with variants
│   ├── Input.tsx       # Form input with validation
│   ├── Modal.tsx       # Modal dialogs
│   ├── Badge.tsx       # Status and label badges
│   ├── Form.tsx        # Form system components
│   ├── Skeleton.tsx    # Loading skeletons
│   ├── Toast.tsx       # Notification system
│   └── README.md       # Component documentation
├── contexts/           # React contexts
│   ├── AuthContext.tsx # Authentication state
│   └── ThemeContext.tsx# Theme management
├── pages/              # Page components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── Agents.tsx      # Agent listing
│   ├── Clients.tsx     # Client management
│   └── ...
├── services/           # API and external services
│   └── api.ts         # API client
├── types/             # TypeScript type definitions
│   └── index.ts       # Shared types
├── utils/             # Utility functions
│   └── cn.ts          # Class name utilities
├── test/              # Test utilities and setup
│   ├── setup.ts       # Test environment setup
│   └── test-utils.tsx # Testing utilities
├── App.tsx            # Main application component
├── index.tsx          # Application entry point
└── index.css          # Global styles
```

## 🎨 Design System

### Theme Configuration
The application supports light/dark mode with system preference detection:

```tsx
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

// Wrap your app
<ThemeProvider>
  <App />
</ThemeProvider>

// Use in components
const { theme, setTheme, actualTheme } = useTheme();
```

### Color Palette
- **Primary**: Blue tones for primary actions
- **Secondary**: Gray tones for secondary elements  
- **Success**: Green for positive states
- **Warning**: Yellow for caution states
- **Error**: Red for error states

### Typography
- **Font**: Inter for UI text, JetBrains Mono for code
- **Scales**: text-xs to text-4xl following Tailwind conventions

### Spacing
Following Tailwind's 4px base spacing system (1 = 4px).

## 🧪 Testing

### Running Tests
```bash
# Run tests in watch mode
npm run test

# Run tests once
npm run test:run

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

### Testing Utilities
Use the custom render function from `test-utils.tsx`:

```tsx
import { render, screen } from '../test/test-utils';
import { Button } from './Button';

test('renders button', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

### Mock Data
Use the provided mock factories:

```tsx
import { mockAgent, mockClient } from '../test/test-utils';

const agent = mockAgent({ name: 'Custom Agent' });
```

## 📝 Code Style

### TypeScript
- Use strict TypeScript configuration
- Define proper interfaces for all props
- Use generic components where appropriate
- Avoid `any` types

### React Patterns
- Use functional components with hooks
- Implement proper error boundaries
- Use React.memo for performance optimization
- Follow the hooks rules

### Naming Conventions
- **Components**: PascalCase (`Button.tsx`)
- **Hooks**: camelCase starting with `use` (`useAuth`)
- **Utilities**: camelCase (`formatDate`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE_URL`)

### File Organization
- One component per file
- Co-locate related files (component + test + styles)
- Use index files for clean imports
- Group by feature, not by file type

## 🔧 Development Workflow

### 1. Component Development
1. Create component in `src/components/`
2. Add TypeScript interfaces
3. Implement accessibility features
4. Add tests in `__tests__/` directory
5. Update component README

### 2. Page Development
1. Create page component in `src/pages/`
2. Add route in `App.tsx`
3. Implement responsive design
4. Add loading and error states
5. Write integration tests

### 3. API Integration
1. Add API methods to `services/api.ts`
2. Define TypeScript types in `types/index.ts`
3. Use React Query for data fetching
4. Handle loading and error states
5. Add proper error boundaries

## 🎯 Best Practices

### Performance
- Use React.memo for expensive components
- Implement proper loading states
- Optimize images and assets
- Use code splitting for large features
- Monitor bundle size

### Accessibility
- Use semantic HTML elements
- Add proper ARIA attributes
- Ensure keyboard navigation
- Test with screen readers
- Maintain color contrast ratios

### Error Handling
- Use error boundaries for component errors
- Show user-friendly error messages
- Log errors for debugging
- Provide recovery actions
- Handle network failures gracefully

### State Management
- Use React Query for server state
- Use React Context for global UI state
- Keep local state in components
- Avoid prop drilling with context
- Use reducers for complex state logic

## 🔍 Code Quality

### Linting
```bash
npm run lint          # Check for issues
npm run lint:fix      # Auto-fix issues
```

### Type Checking
```bash
npm run type-check    # Check TypeScript types
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
- ESLint for code quality
- TypeScript for type checking
- Prettier for code formatting

## 📚 Key Libraries

### Core
- **React 18**: UI library with concurrent features
- **TypeScript**: Type safety and better DX
- **Vite**: Fast build tool and dev server

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: SVG icon library
- **class-variance-authority**: Component variant management

### Data Fetching
- **React Query**: Server state management
- **Axios**: HTTP client

### Forms
- **React Hook Form**: Performant form library

### Routing
- **React Router**: Client-side routing

### Testing
- **Vitest**: Test runner
- **Testing Library**: Testing utilities
- **jsdom**: DOM environment for tests

## 🚀 Build and Deployment

### Development Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Environment Variables
Create `.env.local` for local development:
```
VITE_API_URL=http://localhost:8000
```

## 🐛 Debugging

### Browser DevTools
- Use React DevTools extension
- Monitor network requests
- Check console for errors
- Use performance profiler

### VS Code Setup
Recommended extensions:
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript Importer
- Error Lens

## 📖 Resources

### Documentation
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [React Query](https://tanstack.com/query)

### Tools
- [React DevTools](https://chrome.google.com/webstore/detail/react-developer-tools)
- [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)

## 🤝 Contributing

1. Follow the established patterns and conventions
2. Write tests for new features
3. Update documentation
4. Ensure accessibility compliance
5. Test across different browsers and devices

## 📞 Support

For questions or issues:
- Check the component documentation in `src/components/README.md`
- Review existing tests for examples
- Create an issue in the repository
