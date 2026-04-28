"use client";

import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";

import { cn } from "./utils";

interface ProgressProps extends React.ComponentProps<typeof ProgressPrimitive.Root> {
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

function Progress({
  className,
  value,
  variant = 'default',
  ...props
}: ProgressProps) {
  const variantClasses = {
    default: 'bg-primary',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
  };

  const backgroundClasses = {
    default: 'bg-primary/20',
    success: 'bg-emerald-500/20',
    warning: 'bg-amber-500/20',
    danger: 'bg-red-500/20',
  };

  return (
    <ProgressPrimitive.Root
      data-slot="progress"
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full",
        backgroundClasses[variant],
        className,
      )}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="progress-indicator"
        className={cn(
          "h-full w-full flex-1 transition-all",
          variantClasses[variant],
        )}
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}

export { Progress };
