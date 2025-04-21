import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Button component with various styles and variants
 * 
 * @param {Object} props - Component props
 * @param {string} [props.variant="default"] - Button variant
 * @param {string} [props.size="default"] - Button size
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Button content
 * @returns {JSX.Element} - Button component
 */
const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-primary text-primary-foreground hover:bg-primary/90": variant === "default",
            "bg-destructive text-destructive-foreground hover:bg-destructive/90": variant === "destructive",
            "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground": variant === "outline",
            "bg-secondary text-secondary-foreground hover:bg-secondary/80": variant === "secondary",
            "bg-accent text-accent-foreground hover:bg-accent/80": variant === "accent",
            "bg-transparent underline-offset-4 hover:underline text-primary": variant === "link",
            "bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:from-blue-700 hover:to-indigo-800": variant === "gradient",
            "h-10 px-4 py-2": size === "default",
            "h-9 rounded-md px-3": size === "sm",
            "h-11 rounded-md px-8": size === "lg",
            "h-8 rounded-md px-2 text-xs": size === "xs",
            "w-full": size === "full",
          },
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";

export default Button; 