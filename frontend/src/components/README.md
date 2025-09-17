# A2A Registry UI Components

This directory contains the reusable UI components for the A2A Agent Registry frontend. These components follow modern React patterns and are built with accessibility, performance, and developer experience in mind.

## Design System Components

### Core Components

#### Button (`Button.tsx`)
A flexible button component with multiple variants and states.

**Features:**
- Multiple variants: default, destructive, outline, secondary, ghost, link, success, warning
- Different sizes: xs, sm, default, lg, icon
- Loading states with spinner
- Left/right icon support
- Full-width option
- Accessibility compliant

**Usage:**
```tsx
import { Button } from './components/Button';

<Button variant="primary" size="lg" loading={isSubmitting}>
  Submit Form
</Button>
```

#### Input (`Input.tsx`)
Enhanced input component with validation states and accessibility features.

**Features:**
- Multiple variants: default, error, success
- Different sizes: sm, default, lg
- Label and hint text support
- Error message display
- Left/right icons
- Password toggle functionality
- Accessibility compliant with ARIA attributes

**Usage:**
```tsx
import { Input } from './components/Input';

<Input
  label="Email Address"
  type="email"
  error={errors.email?.message}
  hint="We'll never share your email"
  leftIcon={<EmailIcon />}
/>
```

#### Badge (`Badge.tsx`)
Flexible badge component for status indicators and labels.

**Features:**
- Multiple variants with semantic colors
- Different sizes
- Removable badges
- Icon support
- Pre-built status and priority badges

**Usage:**
```tsx
import { Badge, StatusBadge, PriorityBadge } from './components/Badge';

<Badge variant="success">Active</Badge>
<StatusBadge status="active" />
<PriorityBadge priority="high" />
```

#### Modal (`Modal.tsx`)
Accessible modal component with backdrop and focus management.

**Features:**
- Multiple sizes: sm, md, lg, xl, full
- Backdrop click and ESC key handling
- Focus trap and restoration
- Custom footer support
- Confirmation modal variant
- Accessibility compliant

**Usage:**
```tsx
import Modal, { ConfirmationModal } from './components/Modal';

<Modal isOpen={isOpen} onClose={onClose} title="Settings">
  <p>Modal content here</p>
</Modal>

<ConfirmationModal
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  onConfirm={handleDelete}
  title="Delete Item"
  message="Are you sure you want to delete this item?"
  variant="danger"
/>
```

#### Form Components (`Form.tsx`)
Comprehensive form system built on React Hook Form.

**Features:**
- Type-safe form handling
- Validation integration
- Form groups and sections
- Error and success states
- Consistent styling

**Usage:**
```tsx
import { Form, FormField, FormGroup, FormActions, SubmitButton } from './components/Form';

<Form onSubmit={handleSubmit} options={{ defaultValues }}>
  {({ register, formState: { errors } }) => (
    <>
      <FormGroup title="Personal Information">
        <FormField>
          <Input
            {...register('name', { required: 'Name is required' })}
            label="Full Name"
            error={errors.name?.message}
          />
        </FormField>
      </FormGroup>
      
      <FormActions>
        <Button variant="outline">Cancel</Button>
        <SubmitButton>Save Changes</SubmitButton>
      </FormActions>
    </>
  )}
</Form>
```

### Loading Components

#### Skeleton (`Skeleton.tsx`)
Skeleton loading components for better perceived performance.

**Features:**
- Basic skeleton with customizable dimensions
- Pre-built patterns: CardSkeleton, TableSkeleton, StatsSkeleton
- Accessibility compliant with proper ARIA labels

**Usage:**
```tsx
import { Skeleton, CardSkeleton, StatsSkeleton } from './components/Skeleton';

{isLoading ? <CardSkeleton /> : <ActualCard />}
{isLoading ? <StatsSkeleton /> : <StatsGrid />}
```

#### LoadingSpinner (`LoadingSpinner.tsx`)
Animated loading spinner with customizable text.

### Toast System (`Toast.tsx`)
Enhanced toast notification system with multiple variants.

**Features:**
- Success, error, warning, info, and loading toasts
- Promise-based toasts for async operations
- Custom notification toasts with actions
- Dismissible notifications
- Consistent styling and animations

**Usage:**
```tsx
import { showToast, showNotification } from './components/Toast';

// Simple toasts
showToast.success('Data saved successfully!');
showToast.error('Something went wrong');

// Promise toast
showToast.promise(
  saveData(),
  {
    loading: 'Saving...',
    success: 'Saved!',
    error: 'Failed to save'
  }
);

// Custom notification
showNotification({
  title: 'New Update Available',
  message: 'Version 2.0 is now available',
  type: 'info',
  action: {
    label: 'Update Now',
    onClick: handleUpdate
  }
});
```

## Layout Components

#### Layout (`Layout.tsx`)
Main application layout with navigation and user management.

#### ProtectedRoute (`ProtectedRoute.tsx`)
Route wrapper for authentication-based access control.

## Specialized Components

#### AgentCard (`AgentCard.tsx`)
Card component specifically for displaying agent information.

#### SearchBar (`SearchBar.tsx`)
Search input with filtering capabilities.

#### StatsCard (`StatsCard.tsx`)
Card component for displaying statistics and metrics.

## Utility Functions (`utils/cn.ts`)

The `cn` utility function combines `clsx` and `tailwind-merge` for optimal class handling:

```tsx
import { cn } from '../utils/cn';

<div className={cn(
  'base-classes',
  condition && 'conditional-classes',
  className
)} />
```

Additional utilities:
- `formatBytes`: Format file sizes
- `debounce`: Debounce function calls
- `truncate`: Truncate text with ellipsis
- `formatDate`: Format dates consistently
- `formatRelativeTime`: Relative time formatting
- `copyToClipboard`: Copy text to clipboard

## Theme System

The application supports light/dark mode with system preference detection:

```tsx
import { ThemeProvider, useTheme, ThemeToggle } from '../contexts/ThemeContext';

// Wrap your app
<ThemeProvider>
  <App />
</ThemeProvider>

// Use in components
const { theme, setTheme, actualTheme } = useTheme();

// Theme toggle component
<ThemeToggle />
```

## Best Practices

1. **Accessibility**: All components include proper ARIA attributes, keyboard navigation, and screen reader support.

2. **Performance**: Components use React.memo, useCallback, and useMemo where appropriate to prevent unnecessary re-renders.

3. **Type Safety**: Full TypeScript support with proper prop types and generic components.

4. **Consistency**: All components follow the same design patterns and use the design system tokens.

5. **Responsive Design**: Components are mobile-first and work across all screen sizes.

6. **Testing**: Components are designed to be easily testable with clear props and predictable behavior.

## Development Guidelines

- Use the design system components instead of creating custom ones
- Follow the established patterns for new components
- Include proper TypeScript types
- Add accessibility features (ARIA labels, keyboard navigation)
- Test components across different themes and screen sizes
- Document new components and their props
- Use the utility functions for common operations
