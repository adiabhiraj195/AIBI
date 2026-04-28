import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, User, CheckCircle, Brain } from 'lucide-react';

export default function RegisterPage() {
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        confirm_password: '',
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const validateForm = () => {
        if (!formData.email || !formData.email.includes('@')) {
            setError('Please enter a valid email address');
            return false;
        }
        if (!formData.username || formData.username.length < 3) {
            setError('Username must be at least 3 characters long');
            return false;
        }
        if (!formData.password || formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return false;
        }
        if (formData.password !== formData.confirm_password) {
            setError('Passwords do not match');
            return false;
        }
        return true;
    };

    // Helper to get friendly error messages
    const getFriendlyErrorMessage = (error: any) => {
        const message = error.message || '';

        if (message.includes('409') || message.toLowerCase().includes('already exists')) {
            return 'This username is already taken. Please choose another one.';
        }
        if (message.includes('Failed to fetch') || message.includes('Network Error')) {
            return 'Unable to connect to the server. Please check your internet connection.';
        }
        if (message.includes('400') || message.includes('422')) {
            return 'Invalid registration details. Please check your inputs.';
        }

        return message || 'Registration failed. Please try again.';
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);

        try {
            await register(formData);
            setShowSuccess(true);

            // Redirect to login after 2 seconds
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err: any) {
            console.error('Registration error:', err);
            setError(getFriendlyErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    };

    if (showSuccess) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 px-4">
                <div className="max-w-md w-full text-center space-y-6 bg-slate-900/80 p-8 rounded-2xl shadow-2xl border border-emerald-500/30 backdrop-blur">
                    <div className="flex justify-center">
                        <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center animate-pulse shadow-lg shadow-emerald-500/40">
                            <CheckCircle className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white">Account Created!</h2>
                        <p className="mt-2 text-sm text-slate-300">
                            Your account has been successfully created. Redirecting to login...
                        </p>
                    </div>
                    <div className="pt-4">
                        <Link
                            to="/login"
                            className="inline-block px-6 py-2 bg-gradient-to-r from-emerald-600 to-emerald-700 text-white rounded-lg font-medium hover:from-emerald-500 hover:to-emerald-600 transition-all shadow-md hover:shadow-lg"
                        >
                            Go to Login
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 px-4 py-8">
            <div className="max-w-md w-full space-y-6 bg-slate-900/80 p-8 rounded-2xl shadow-2xl border border-slate-700/70 backdrop-blur">
                {/* Header */}
                <div className="text-center space-y-2">
                    <div className="flex justify-center mb-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                            <Brain className="w-7 h-7 text-white" />
                        </div>
                    </div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white via-emerald-100 to-emerald-300 bg-clip-text text-transparent">
                        Create Account
                    </h2>
                    <p className="text-sm text-slate-300">
                        Sign up to start using your Green.co CFO AI Assistant
                    </p>
                </div>

                {/* Register Form */}
                <form className="space-y-4" onSubmit={handleSubmit}>
                    {/* Email Input */}
                    <div className="space-y-2">
                        <label htmlFor="email" className="block text-sm font-semibold text-slate-200">
                            Email Address
                        </label>
                        <div className="relative">
                            <User className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={formData.email}
                                onChange={handleChange}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-700/80 rounded-lg bg-slate-900/60 placeholder-slate-500 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                placeholder="name@example.com"
                            />
                        </div>
                    </div>

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
                                value={formData.username}
                                onChange={handleChange}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-700/80 rounded-lg bg-slate-900/60 placeholder-slate-500 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                placeholder="Choose a username"
                            />
                        </div>
                        <p className="text-xs text-slate-400">At least 3 characters</p>
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
                                autoComplete="new-password"
                                required
                                value={formData.password}
                                onChange={handleChange}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-700/80 rounded-lg bg-slate-900/60 placeholder-slate-500 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                placeholder="Create a strong password"
                            />
                        </div>
                        <p className="text-xs text-slate-400">At least 8 characters recommended</p>
                    </div>

                    {/* Confirm Password Input */}
                    <div className="space-y-2">
                        <label htmlFor="confirm_password" className="block text-sm font-semibold text-slate-200">
                            Confirm Password
                        </label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                            <input
                                id="confirm_password"
                                name="confirm_password"
                                type="password"
                                autoComplete="new-password"
                                required
                                value={formData.confirm_password}
                                onChange={handleChange}
                                className="w-full pl-10 pr-4 py-2.5 border border-slate-700/80 rounded-lg bg-slate-900/60 placeholder-slate-500 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                placeholder="Re-enter your password"
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
                        disabled={isLoading}
                        className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-sm font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg"
                    >
                        {isLoading ? (
                            <div className="flex items-center space-x-2">
                                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Creating account...</span>
                            </div>
                        ) : (
                            'Create Account'
                        )}
                    </button>
                </form>

                {/* Divider */}
                <div className="flex items-center space-x-3">
                    <div className="flex-1 h-px bg-slate-700"></div>
                    <span className="text-xs text-slate-400 font-medium">OR</span>
                    <div className="flex-1 h-px bg-slate-700"></div>
                </div>

                {/* Login Link */}
                <div className="text-center">
                    <p className="text-sm text-slate-300">
                        Already have an account?{' '}
                        <Link to="/login" className="font-semibold text-emerald-400 hover:text-emerald-300 transition-colors">
                            Sign in
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
