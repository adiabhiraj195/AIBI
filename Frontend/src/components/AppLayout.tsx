import { useState, ReactNode } from 'react';
import Sidebar from './Sidebar';
import { ChatSession } from '../types';

interface AppLayoutProps {
    children: ReactNode;
    sessions?: ChatSession[];
    currentSessionId?: string;
    onNewChat?: () => void;
    onSessionSelect?: (sessionId: string) => void;
}

export default function AppLayout({ children, sessions, currentSessionId, onNewChat, onSessionSelect }: AppLayoutProps) {
    const [collapsed, setCollapsed] = useState(true);

    return (
        <div className="min-h-screen flex bg-slate-900 text-slate-100">
            <Sidebar
                collapsed={collapsed}
                onToggle={() => setCollapsed((prev) => !prev)}
                sessions={sessions}
                currentSessionId={currentSessionId}
                onNewChat={onNewChat}
                onSessionSelect={onSessionSelect}
            />
            <main className="flex-1 min-h-screen overflow-y-auto">
                <div className="w-full">{children}</div>
            </main>
        </div>
    );
}
