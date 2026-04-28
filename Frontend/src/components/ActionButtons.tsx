import React, { useState } from 'react';
import { Activity, Bell, Mail, LayoutDashboard } from 'lucide-react';
import { TrackMonitorPopup } from './popups/TrackMonitorPopup';
import { ReminderPopup } from './popups/ReminderPopup';
import { EmailPopup } from './popups/EmailPopup';
import { Toast } from './popups/Toast';

import { DashboardPinModal } from './DashboardPinModal';

interface ActionButtonsProps {
  messageContent: string;
  visualizations?: any[];
}

export function ActionButtons({ messageContent, visualizations }: ActionButtonsProps) {
  const [showTrackPopup, setShowTrackPopup] = useState(false);
  const [showReminderPopup, setShowReminderPopup] = useState(false);
  const [showEmailPopup, setShowEmailPopup] = useState(false);
  const [showPinModal, setShowPinModal] = useState(false); // Added state
  const [showToast, setShowToast] = useState(false);

  // New handler for pinning
  const handlePinConfirm = async (title: string, category: string) => {
    if (visualizations && visualizations.length > 0) {
      try {
        const { saveDashboardItem } = await import('../services/api');
        await saveDashboardItem(title, visualizations[0], messageContent, category);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 2000);
      } catch (e) {
        console.error("Failed to save", e);
      }
    }
  };

  return (
    <>
      <div className="flex gap-3 mt-4">
        <button
          onClick={() => setShowTrackPopup(true)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-xl font-medium transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/50 hover:scale-105"
        >
          <Activity className="w-5 h-5" />
          Track / Monitor
        </button>

        <button
          onClick={() => setShowReminderPopup(true)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-xl font-medium transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/50 hover:scale-105"
        >
          <Bell className="w-5 h-5" />
          Set Reminder
        </button>

        <button
          onClick={() => setShowEmailPopup(true)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-xl font-medium transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/50 hover:scale-105"
        >
          <Mail className="w-5 h-5" />
          Send Mail
        </button>

        {visualizations && visualizations.length > 0 && (
          <button
            onClick={() => setShowPinModal(true)}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white rounded-xl font-medium transition-all shadow-lg shadow-amber-500/20 hover:shadow-amber-500/50 hover:scale-105"
          >
            <LayoutDashboard className="w-5 h-5" />
            Pin to Dashboard
          </button>
        )}
      </div>

      {/* Popups */}
      {showTrackPopup && (
        <TrackMonitorPopup
          onClose={() => setShowTrackPopup(false)}
          messageContent={messageContent}
          visualizations={visualizations}
        />
      )}

      {showReminderPopup && (
        <ReminderPopup
          onClose={() => setShowReminderPopup(false)}
          messageContent={messageContent}
        />
      )}

      {showEmailPopup && (
        <EmailPopup
          onClose={() => setShowEmailPopup(false)}
          messageContent={messageContent}
        />
      )}

      {/* Pin Modal */}
      <DashboardPinModal
        isOpen={showPinModal}
        onClose={() => setShowPinModal(false)}
        onConfirm={handlePinConfirm}
        initialTitle={`Visualization ${new Date().toLocaleDateString()}`}
      />

      {showToast && <Toast message="Added to dashboard!" />}
    </>
  );
}
