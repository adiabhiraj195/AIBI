import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Plus, FolderOpen, Settings, Trash2, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useAuth } from '../context/AuthContext';

interface Workspace {
    id: string;
    name: string;
    description: string;
    createdAt: Date;
    itemCount: number;
}

export default function WorkspacePage() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [workspaces, setWorkspaces] = useState<Workspace[]>([
        {
            id: '1',
            name: 'Financial Analysis 2024',
            description: 'Q4 2024 financial metrics and revenue analysis',
            createdAt: new Date('2024-10-15'),
            itemCount: 24
        },
        {
            id: '2',
            name: 'Project Management',
            description: 'Ongoing projects and timeline tracking',
            createdAt: new Date('2024-11-02'),
            itemCount: 12
        },
        {
            id: '3',
            name: 'Risk Assessment',
            description: 'Market risk and operational risk analysis',
            createdAt: new Date('2024-12-01'),
            itemCount: 8
        }
    ]);

    const [isCreating, setIsCreating] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');

    const handleCreateWorkspace = () => {
        if (newWorkspaceName.trim()) {
            const newWorkspace: Workspace = {
                id: Date.now().toString(),
                name: newWorkspaceName,
                description: 'New workspace',
                createdAt: new Date(),
                itemCount: 0
            };
            setWorkspaces([newWorkspace, ...workspaces]);
            setNewWorkspaceName('');
            setIsCreating(false);
        }
    };

    const handleDeleteWorkspace = (id: string) => {
        setWorkspaces(workspaces.filter(w => w.id !== id));
    };

    const handleOpenWorkspace = (id: string) => {
        navigate(`/dashboard`);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 text-white">
            {/* Header */}
            <header className="border-b border-slate-800/50 backdrop-blur-sm">
                <div className="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
                            <Brain className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-white text-xl font-semibold">Green.co CFO AI Assistant</h1>
                            <p className="text-emerald-400 text-sm">Workspace Management</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <p className="text-sm text-slate-300">{user?.name || user?.username}</p>
                            <p className="text-xs text-slate-500">{user?.email}</p>
                        </div>
                        <button
                            onClick={() => {
                                logout();
                                navigate('/login');
                            }}
                            className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white bg-slate-800/50 hover:bg-slate-800 rounded-lg transition-colors border border-slate-700/50"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-8 py-12">
                {/* Page Title */}
                <div className="mb-12">
                    <h2 className="text-4xl font-bold mb-2">Your Workspaces</h2>
                    <p className="text-slate-400">
                        Create and manage your analysis workspaces. Each workspace contains your queries, data mappings, and insights.
                    </p>
                </div>

                {/* Create New Workspace Section */}
                {!isCreating ? (
                    <button
                        onClick={() => setIsCreating(true)}
                        className="mb-12 flex items-center gap-3 w-full md:w-auto px-6 py-4 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 rounded-xl font-medium text-white transition-all shadow-lg hover:shadow-xl"
                    >
                        <Plus className="w-5 h-5" />
                        Create New Workspace
                    </button>
                ) : (
                    <div className="mb-12 p-6 bg-slate-900/70 border border-emerald-500/20 rounded-xl backdrop-blur-sm">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold text-slate-200 mb-2">
                                    Workspace Name
                                </label>
                                <input
                                    type="text"
                                    value={newWorkspaceName}
                                    onChange={(e) => setNewWorkspaceName(e.target.value)}
                                    placeholder="Enter workspace name"
                                    className="w-full px-4 py-2.5 border border-slate-700/50 rounded-lg bg-slate-800/50 placeholder-slate-500 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                    onKeyPress={(e) => e.key === 'Enter' && handleCreateWorkspace()}
                                    autoFocus
                                />
                            </div>
                            <div className="flex gap-3">
                                <Button
                                    onClick={handleCreateWorkspace}
                                    className="bg-emerald-600 hover:bg-emerald-700 text-white"
                                >
                                    Create Workspace
                                </Button>
                                <Button
                                    onClick={() => setIsCreating(false)}
                                    variant="outline"
                                    className="border-slate-700 bg-slate-800/50 text-slate-300 hover:text-white hover:bg-slate-800"
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Workspaces Grid */}
                {workspaces.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {workspaces.map((workspace) => (
                            <div
                                key={workspace.id}
                                className="group bg-slate-900/70 border border-slate-800/50 rounded-xl p-6 hover:border-emerald-500/30 transition-all hover:shadow-lg hover:shadow-emerald-500/10"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="w-10 h-10 bg-emerald-500/10 rounded-lg flex items-center justify-center group-hover:bg-emerald-500/20 transition-colors">
                                        <FolderOpen className="w-5 h-5 text-emerald-400" />
                                    </div>
                                    <button
                                        onClick={() => handleDeleteWorkspace(workspace.id)}
                                        className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-red-500/10 rounded-lg text-red-400 hover:text-red-300"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>

                                <h3 className="text-lg font-semibold text-white mb-2">
                                    {workspace.name}
                                </h3>
                                <p className="text-sm text-slate-400 mb-4">
                                    {workspace.description}
                                </p>

                                <div className="flex items-center justify-between mb-4 pt-4 border-t border-slate-700/50">
                                    <div className="text-xs text-slate-500">
                                        <p>Created {workspace.createdAt.toLocaleDateString()}</p>
                                        <p className="mt-1">{workspace.itemCount} items</p>
                                    </div>
                                </div>

                                <button
                                    onClick={() => handleOpenWorkspace(workspace.id)}
                                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 rounded-lg font-medium text-white transition-all"
                                >
                                    Open Workspace
                                    <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16">
                        <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FolderOpen className="w-8 h-8 text-slate-500" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-300 mb-2">No Workspaces Yet</h3>
                        <p className="text-slate-400 mb-6">Create your first workspace to get started</p>
                        <Button
                            onClick={() => setIsCreating(true)}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Create Workspace
                        </Button>
                    </div>
                )}
            </main>
        </div>
    );
}
