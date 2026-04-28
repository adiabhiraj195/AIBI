import React from 'react';
import { Star } from 'lucide-react';

interface ToastProps {
  message: string;
}

export function Toast({ message }: ToastProps) {
  return (
    <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300">
      <div className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 border border-amber-400/30">
        <div className="p-1 bg-white/20 rounded-lg">
          <Star className="w-5 h-5 fill-white" />
        </div>
        <span className="font-medium">{message}</span>
      </div>
    </div>
  );
}
