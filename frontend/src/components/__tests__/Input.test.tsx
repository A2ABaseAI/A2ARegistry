import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../../test/test-utils';
import { Input } from '../Input';

describe('Input', () => {
  it('renders with basic props', () => {
    render(<Input placeholder="Enter text" />);
    const input = screen.getByPlaceholderText('Enter text');
    expect(input).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Input label="Email Address" />);
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<Input label="Email" error="Email is required" />);
    const input = screen.getByLabelText('Email');
    expect(input).toHaveClass('border-red-300');
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(input).toHaveAttribute('aria-invalid', 'true');
  });

  it('shows success state', () => {
    render(<Input label="Email" success="Email is valid" />);
    const input = screen.getByLabelText('Email');
    expect(input).toHaveClass('border-green-300');
    expect(screen.getByText('Email is valid')).toBeInTheDocument();
  });

  it('shows hint text', () => {
    render(<Input label="Password" hint="Must be at least 8 characters" />);
    expect(screen.getByText('Must be at least 8 characters')).toBeInTheDocument();
  });

  it('handles password toggle', () => {
    render(<Input type="password" showPasswordToggle />);
    // Password inputs don't have role="textbox", they have their own role
    const input = document.querySelector('input[type="password"]') as HTMLInputElement;
    const toggleButton = screen.getByLabelText('Show password');

    expect(input).toHaveAttribute('type', 'password');

    fireEvent.click(toggleButton);
    expect(input).toHaveAttribute('type', 'text');
    expect(screen.getByLabelText('Hide password')).toBeInTheDocument();

    fireEvent.click(toggleButton);
    expect(input).toHaveAttribute('type', 'password');
  });

  it('renders with icons', () => {
    const LeftIcon = () => <span data-testid="left-icon">@</span>;
    const RightIcon = () => <span data-testid="right-icon">✓</span>;

    render(<Input leftIcon={<LeftIcon />} rightIcon={<RightIcon />} />);
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
  });

  it('handles different sizes', () => {
    const { rerender } = render(<Input size="sm" />);
    expect(screen.getByRole('textbox')).toHaveClass('h-9');

    rerender(<Input size="lg" />);
    expect(screen.getByRole('textbox')).toHaveClass('h-11');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('generates unique IDs', () => {
    render(
      <div>
        <Input label="First" />
        <Input label="Second" />
      </div>
    );

    const firstInput = screen.getByLabelText('First');
    const secondInput = screen.getByLabelText('Second');
    
    expect(firstInput.id).not.toBe(secondInput.id);
  });

  it('uses provided ID', () => {
    render(<Input id="custom-id" label="Test" />);
    expect(screen.getByLabelText('Test')).toHaveAttribute('id', 'custom-id');
  });

  it('associates error with input via aria-describedby', () => {
    render(<Input label="Email" error="Invalid email" />);
    const input = screen.getByLabelText('Email');
    const errorId = input.getAttribute('aria-describedby');
    expect(errorId).toBeTruthy();
    expect(screen.getByText('Invalid email')).toHaveAttribute('id', errorId);
  });
});
