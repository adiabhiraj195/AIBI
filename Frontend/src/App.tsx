import { Routes, Route, Navigate, Outlet, useOutletContext } from 'react-router-dom';
export type { Message, ChatSession, SystemStatus } from './types';
import ChatPage from './pages/ChatPage';
import WelcomeRoutePage from './pages/WelcomeRoutePage';
import WorkspacePage from './pages/WorkspacePage';
import DashboardRoutePage from './pages/DashboardRoutePage';
import UploadedDataPage from './pages/UploadedDataPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/AppLayout';
import { ChatSession } from './types';

export interface AppLayoutContext {
  setSessions?: (sessions: ChatSession[]) => void;
  setCurrentSessionId?: (id: string) => void;
  setOnNewChat?: (handler: () => void) => void;
  setOnSessionSelect?: (handler: (id: string) => void) => void;
}

function ProtectedAppLayout() {
  return (
    <ProtectedRoute>
      <Outlet />
    </ProtectedRoute>
  );
}

export function useAppLayout() {
  return useOutletContext<AppLayoutContext>();
}

import PublicRoute from './components/PublicRoute';

// ... (imports remain matching existing file)

export default function App() {
  return (
    <AuthProvider>
      <div className='relative'>
        <Routes>
          <Route path="/" element={<AppLayout><WelcomeRoutePage /></AppLayout>} />
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
          <Route path="/workspace" element={<ProtectedRoute><AppLayout><WorkspacePage /></AppLayout></ProtectedRoute>} />
          <Route element={<ProtectedAppLayout />}>
            <Route path="/change-password" element={<AppLayout><ChangePasswordPage /></AppLayout>} />
            <Route path="/dashboard" element={<AppLayout><DashboardRoutePage /></AppLayout>} />
            <Route path="/uploaded-data" element={<AppLayout><UploadedDataPage /></AppLayout>} />
          </Route>
          <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}