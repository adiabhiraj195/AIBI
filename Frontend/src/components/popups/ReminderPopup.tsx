import React, { useState, useEffect } from 'react';
import { X, Bell, Clock, Calendar, CheckCircle } from 'lucide-react';

interface ReminderPopupProps {
  onClose: () => void;
  messageContent: string;
}

export function ReminderPopup({ onClose, messageContent }: ReminderPopupProps) {
  const [reminderTime, setReminderTime] = useState('30');
  const [customTime, setCustomTime] = useState('');
  const [reminderSet, setReminderSet] = useState(false);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const handleSetReminder = () => {
    setReminderSet(true);
    setTimeout(() => {
      onClose();
    }, 2000);
  };

  const timeOptions = [
    { value: '15', label: '15 minutes' },
    { value: '30', label: '30 minutes' },
    { value: '60', label: '1 hour' },
    { value: '120', label: '2 hours' },
    { value: '1440', label: '1 day' },
    { value: 'custom', label: 'Custom' },
  ];

  if (reminderSet) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full p-8 text-center animate-in zoom-in-95 duration-200">
          <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-emerald-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Reminder Set!</h3>
          <p className="text-gray-400">
            You'll be notified in {reminderTime === 'custom' ? customTime : timeOptions.find(o => o.value === reminderTime)?.label}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/20">
              <Bell className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-white">Set Reminder</h3>
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
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <p className="text-sm text-gray-400 mb-1">Reminder about:</p>
            <p className="text-white text-sm line-clamp-2">{messageContent.substring(0, 100)}...</p>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm text-gray-300 mb-3">
              <Clock className="w-4 h-4" />
              Remind me in:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {timeOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setReminderTime(option.value)}
                  className={`px-4 py-3 rounded-lg border transition-all ${
                    reminderTime === option.value
                      ? 'bg-purple-500/20 border-purple-500 text-white'
                      : 'bg-gray-800 border-gray-700 text-white hover:border-gray-600'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {reminderTime === 'custom' && (
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-300 mb-2">
                <Calendar className="w-4 h-4" />
                Custom time:
              </label>
              <input
                type="datetime-local"
                value={customTime}
                onChange={(e) => setCustomTime(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSetReminder}
            className="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-medium transition-colors"
          >
            Set Reminder
          </button>
        </div>
      </div>
    </div>
  );
}
