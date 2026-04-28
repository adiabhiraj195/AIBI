import { useMemo } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
    ChevronLeft,
    ChevronRight,
    LayoutDashboard,
    MessageCircle,
    UploadCloud,
    Lock,
    LogOut,
    Sparkles,
    Home,
    FolderOpen,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { ChatSession } from '../types';
import { QueryHistory } from './QueryHistory';
import { ScrollArea } from './ui/scroll-area';
import { Button } from './ui/button';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
    sessions?: ChatSession[];
    currentSessionId?: string;
    onNewChat?: () => void;
    onSessionSelect?: (sessionId: string) => void;
}

const navItems = [
    { label: 'Home', to: '/', icon: Home },
    { label: 'Workspaces', to: '/workspace', icon: FolderOpen },
    { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
    { label: 'Chat', to: '/chat', icon: MessageCircle },
    { label: 'Uploaded Data', to: '/uploaded-data', icon: UploadCloud },
    { label: 'Change Password', to: '/change-password', icon: Lock },
];

function getInitials(name?: string, username?: string) {
    const source = name || username || '';
    if (!source) return 'US';
    const parts = source.split(' ').filter(Boolean);
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return source.slice(0, 2).toUpperCase();
}

export default function Sidebar({ collapsed, onToggle, sessions, currentSessionId, onNewChat, onSessionSelect }: SidebarProps) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const initials = useMemo(() => getInitials(user?.name, user?.username), [user]);
    const isChatPage = location.pathname === '/chat';

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside
            className={`${collapsed ? 'w-20' : 'w-64'} bg-slate-950 border-r border-slate-800 text-slate-100 flex flex-col transition-all duration-300 max-h-screen h-screen sticky z-50`}
        >
            <div className="flex items-center justify-between px-3 py-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center text-white font-semibold shadow-lg shadow-emerald-500/30">
                        {(user?.name || user?.username)?.[0]?.toUpperCase() || 'S'}
                    </div>
                    {!collapsed && (
                        <div className="leading-tight">
                            <p className="text-sm font-semibold text-white">Green.co Copilot</p>
                            <p className="text-xs text-slate-400">AI Assistant</p>
                        </div>
                    )}
                </div>
                <button
                    type="button"
                    onClick={onToggle}
                    className=" ml-1 items-center justify-center h-9 w-9 grid place-items-center rounded-lg border border-slate-800 bg-slate-900/60 text-slate-300 hover:text-white hover:border-slate-700 transition"
                    aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                    {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                </button>
            </div>

            <nav className="flex-1 px-2 space-y-1 flex flex-col overflow-hidden">
                <div className="space-y-1">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                title={item.label}
                                className={({ isActive }) =>
                                    [
                                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                        collapsed ? 'justify-center' : '',
                                        isActive
                                            ? 'bg-emerald-500/15 text-emerald-300'
                                            : 'text-slate-300 hover:text-white hover:bg-slate-900/60',
                                    ]
                                        .filter(Boolean)
                                        .join(' ')
                                }
                            >
                                <Icon className="h-4 w-4" />
                                {!collapsed && <span>{item.label}</span>}
                            </NavLink>
                        );
                    })}
                </div>

                {!collapsed && isChatPage && onNewChat && (
                    <>
                        <div className="pt-3 pb-2">
                            <Button onClick={onNewChat} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white">
                                <Sparkles className="w-4 h-4 mr-2" />
                                New Chat
                            </Button>
                        </div>

                        {sessions && sessions.length > 0 && (
                            <div className="flex-1 overflow-hidden flex flex-col min-h-0">
                                <div className="pt-3 pb-2 border-t border-slate-800">
                                    <h3 className="text-xs text-slate-500 uppercase tracking-wider px-1">Recent Sessions</h3>
                                </div>
                                <ScrollArea className="flex-1">
                                    <QueryHistory
                                        sessions={sessions}
                                        onSessionSelect={onSessionSelect}
                                        currentSessionId={currentSessionId}
                                    />
                                </ScrollArea>
                            </div>
                        )}
                    </>
                )}
            </nav>

            <div className="border-t border-slate-800 px-3 py-4 space-y-3 items-center flex flex-col">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-slate-800 text-xs font-semibold text-emerald-300 grid place-items-center">
                        {initials}
                    </div>
                    {!collapsed && (
                        <div className="min-w-0">
                            <p className="text-sm font-semibold text-white truncate">{user?.name || user?.username || 'User'}</p>
                            {user?.email && <p className="text-xs text-slate-400 truncate">{user.email}</p>}
                        </div>
                    )}
                </div>
                <button
                    type="button"
                    onClick={handleLogout}
                    className={`w-full inline-flex items-center ${collapsed ? 'justify-center' : 'justify-start'} gap-2 rounded-lg px-3 py-2 text-sm font-semibold text-emerald-300 bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/15 transition`}
                >
                    <LogOut className="h-4 w-4" />
                    {!collapsed && <span>Logout</span>}
                </button>
            </div>
        </aside>
    );
}
