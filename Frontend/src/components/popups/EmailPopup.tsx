import React, { useState, useEffect } from 'react';
import { X, Mail, Send, Paperclip, CheckCircle } from 'lucide-react';

interface EmailPopupProps {
  onClose: () => void;
  messageContent: string;
}

export function EmailPopup({ onClose, messageContent }: EmailPopupProps) {
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('Wind Energy Analysis Report');
  const [body, setBody] = useState(`Hi,\n\nI wanted to share this analysis with you:\n\n${messageContent.substring(0, 200)}...\n\nBest regards`);
  const [emailSent, setEmailSent] = useState(false);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const handleSend = () => {
    if (!to.trim()) return;
    setEmailSent(true);
    setTimeout(() => {
      onClose();
    }, 2000);
  };

  if (emailSent) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full p-8 text-center animate-in zoom-in-95 duration-200">
          <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-emerald-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Email Sent!</h3>
          <p className="text-gray-400">
            Your message has been sent to {to}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-2xl w-full animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/20">
              <Mail className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="text-xl font-semibold text-white">New Message</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* To Field */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">To:</label>
            <input
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="recipient@example.com"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>

          {/* Subject Field */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Subject:</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>

          {/* Body Field */}
          <div>
            <label className="text-sm text-gray-400 mb-2 block">Message:</label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={8}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors resize-none"
            />
          </div>

          {/* Attachment Info */}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Paperclip className="w-4 h-4" />
            <span>Analysis data will be attached</span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex gap-3">
          <button
            onClick={onClose}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSend}
            disabled={!to.trim()}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            Send Email
          </button>
        </div>
      </div>
    </div>
  );
}
