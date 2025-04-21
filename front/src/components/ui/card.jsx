import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Card container component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Card content
 * @returns {JSX.Element} - Card component
 */
const Card = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border bg-card text-card-foreground shadow-sm glass",
        className
      )}
      {...props}
    />
  )
);
Card.displayName = "Card";

/**
 * Card header component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Card header content
 * @returns {JSX.Element} - Card header component
 */
const CardHeader = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col space-y-1.5 p-6", className)}
      {...props}
    />
  )
);
CardHeader.displayName = "CardHeader";

/**
 * Card title component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Card title content
 * @returns {JSX.Element} - Card title component
 */
const CardTitle = React.forwardRef(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn(
        "text-2xl font-semibold leading-none tracking-tight",
        className
      )}
      {...props}
    />
  )
);
CardTitle.displayName = "CardTitle";

/**
 * Card description component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Card description content
 * @returns {JSX.Element} - Card description component
 */
const CardDescription = React.forwardRef(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
);
CardDescription.displayName = "CardDescription";

/**
 * Card content component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Card content
 * @returns {JSX.Element} - Card content component
 */
const CardContent = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  )
);
CardContent.displayName = "CardContent";

/**
 * Card footer component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} props.children - Card footer content
 * @returns {JSX.Element} - Card footer component
 */
const CardFooter = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center p-6 pt-0", className)}
      {...props}
    />
  )
);
CardFooter.displayName = "CardFooter";

/**
 * Card logs component for displaying recent activity with a "View all" button
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Title of the activity section
 * @param {React.ReactNode} props.children - Card logs content
 * @param {Function} props.onViewAll - Function to call when "View all" is clicked
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} - Card logs component
 */
const CardLogs = React.forwardRef(
  ({ title, children, onViewAll, className, ...props }, ref) => (
    <Card ref={ref} className={cn("overflow-hidden", className)} {...props}>
      <div className="flex justify-between items-center p-6 pb-2">
        <CardTitle className="text-xl">{title}</CardTitle>
        {onViewAll && (
          <button 
            onClick={onViewAll}
            className="text-sm text-primary hover:underline focus:outline-none"
          >
            Voir tout
          </button>
        )}
      </div>
      <CardContent>
        {children}
      </CardContent>
    </Card>
  )
);
CardLogs.displayName = "CardLogs";

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardLogs
}; 