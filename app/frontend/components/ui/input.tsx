"use client";

import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = "", ...props }, ref) => {
    return (
      <div className="space-y-1.5">
        {label && (
          <label className="block text-sm font-medium text-slate-700">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`w-full px-4 py-2.5 rounded-xl border transition-all duration-200 text-sm
            ${
              error
                ? "border-danger-500 focus:ring-danger-500 focus:border-danger-500"
                : "border-slate-200 focus:ring-primary-500 focus:border-primary-500"
            }
            focus:outline-none focus:ring-2 focus:ring-offset-0
            placeholder:text-slate-400 bg-white
            ${className}`}
          {...props}
        />
        {error && <p className="text-xs text-danger-500">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
