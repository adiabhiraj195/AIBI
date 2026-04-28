import { useState, FormEvent, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Lock, Brain } from 'lucide-react';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login, isAuthenticated, isLoading: isAuthLoading } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!isAuthLoading && isAuthenticated) {
            navigate('/workspace', { replace: true });
        }
    }, [isAuthenticated, isAuthLoading, navigate]);

    // Helper to get friendly error messages
    const getFriendlyErrorMessage = (error: any) => {
        const message = error.message || '';

        if (message.includes('401') || message.includes('403') || message.toLowerCase().includes('invalid')) {
            return 'Invalid username or password. Please try again.';
        }
        if (message.includes('Failed to fetch') || message.includes('Network Error') || message.includes('503')) {
            return 'Unable to connect to the server. Please check your internet connection.';
        }
        if (message.includes('500')) {
            return 'Server error. Please try again later.';
        }

        return message || 'Login failed. Please try again.';
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login({ username, password });
            navigate('/workspace');
        } catch (err: any) {
            console.error('Login error:', err);
            setError(getFriendlyErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 px-4">
            <div className="max-w-md w-full space-y-8 bg-slate-900/80 p-8 rounded-2xl shadow-2xl border border-slate-700/70 backdrop-blur">
                {/* Header */}
                <div className="text-center space-y-2">
                    <div className="flex justify-center mb-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                            <Brain className="w-7 h-7 text-white" />
                        </div>
                    </div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white via-emerald-100 to-emerald-300 bg-clip-text text-transparent">
                        Welcome Back
                    </h2>
                    <p className="text-sm text-slate-300">
                        Sign in to access your Green.co CFO AI Assistant
                    </p>
                </div>

                {/* Login Form */}
                <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
                    {/* Username Input */}
                    <div className="space-y-2">
                        <label htmlFor="username" className="block text-sm font-semibold text-slate-200">
                            Username
                        </label>
                        <div className="relative">
                            <User className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                            <input
                                id="username"
                                name="username"
                                type="text"
                                autoComplete="username"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-700/80 rounded-lg bg-slate-900/60 placeholder-slate-500 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                placeholder="Enter your username"
                            />
                        </div>
                    </div>

                    {/* Password Input */}
                    <div className="space-y-2">
                        <label htmlFor="password" className="block text-sm font-semibold text-slate-200">
                            Password
                        </label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="current-password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-700/80 rounded-lg bg-slate-900/60 placeholder-slate-500 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                placeholder="Enter your password"
                            />
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/40 text-red-200 px-4 py-3 rounded-lg text-sm flex items-start space-x-2">
                            <span className="text-lg">⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isLoading || !username || !password}
                        className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-sm font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg"
                    >
                        {isLoading ? (
                            <div className="flex items-center space-x-2">
                                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Signing in...</span>
                            </div>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>

                {/* Divider */}
                <div className="flex items-center space-x-3 my-6">
                    <div className="flex-1 h-px bg-slate-700"></div>
                    <span className="text-xs text-slate-400 font-medium">OR</span>
                    <div className="flex-1 h-px bg-slate-700"></div>
                </div>

                {/* Register Link */}
                <div className="text-center space-y-3">
                    <p className="text-sm text-slate-300">
                        Don't have an account?{' '}
                        <Link to="/register" className="font-semibold text-emerald-400 hover:text-emerald-300 transition-colors">
                            Sign up
                        </Link>
                    </p>
                </div>

                {/* Footer */}
                <div className="text-center text-xs text-slate-500 border-t border-slate-800 pt-4">
                    <p>© 2026 Green.co CFO AI Assistant. All rights reserved.</p>
                </div>
            </div>
        </div>
    );
}
