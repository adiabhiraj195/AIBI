import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, ArrowLeft, CheckCircle } from 'lucide-react';

export default function ChangePasswordPage() {
    const [formData, setFormData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: '',
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const { changePassword, user } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const validateForm = () => {
        if (!formData.current_password) {
            setError('Current password is required');
            return false;
        }
        if (!formData.new_password || formData.new_password.length < 8) {
            setError('New password must be at least 8 characters long');
            return false;
        }
        if (formData.new_password !== formData.confirm_password) {
            setError('New passwords do not match');
            return false;
        }
        if (formData.current_password === formData.new_password) {
            setError('New password must be different from current password');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);

        try {
            await changePassword(formData);
            setShowSuccess(true);

            // Reset form
            setFormData({
                current_password: '',
                new_password: '',
                confirm_password: '',
            });

            // Redirect to dashboard after 2 seconds
            setTimeout(() => {
                navigate('/dashboard');
            }, 2000);
        } catch (err: any) {
            setError(err.message || 'Failed to change password. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (showSuccess) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4">
                <div className="max-w-md w-full text-center space-y-6 bg-slate-900 p-8 rounded-2xl shadow-xl border border-emerald-500/20">
                    <div className="flex justify-center">
                        <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center animate-pulse">
                            <CheckCircle className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white">Password Changed!</h2>
                        <p className="mt-2 text-sm text-slate-400">
                            Your password has been successfully updated. Redirecting to dashboard...
                        </p>
                    </div>
                    <div className="pt-4">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="inline-block px-6 py-2 bg-gradient-to-r from-emerald-600 to-emerald-700 text-white rounded-lg font-medium hover:from-emerald-700 hover:to-emerald-800 transition-all"
                        >
                            Go to Dashboard
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
            {/* Main Content */}
            <div className="flex items-center justify-center min-h-[calc(100vh-70px)] px-4 py-8">
                <div className="max-w-md w-full space-y-8 bg-slate-900/70 p-8 rounded-2xl shadow-xl border border-emerald-500/20 backdrop-blur-sm">
                    {/* Header */}
                    <div className="text-center space-y-2">
                        <div className="flex justify-center mb-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
                                <Lock className="w-6 h-6 text-white" />
                            </div>
                        </div>
                        <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-emerald-300 bg-clip-text text-transparent">
                            Change Password
                        </h2>
                        <p className="text-sm text-slate-400">
                            {user?.username && `Update password for ${user.username}`}
                        </p>
                    </div>

                    {/* Password Change Form */}
                    <form className="space-y-5" onSubmit={handleSubmit}>
                        {/* Current Password */}
                        <div className="space-y-2">
                            <label htmlFor="current_password" className="block text-sm font-semibold text-slate-200">
                                Current Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                                <input
                                    id="current_password"
                                    name="current_password"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    value={formData.current_password}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2.5 border border-slate-700/50 rounded-lg placeholder-slate-500 text-white bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                    placeholder="Enter your current password"
                                />
                            </div>
                        </div>

                        {/* New Password */}
                        <div className="space-y-2">
                            <label htmlFor="new_password" className="block text-sm font-semibold text-slate-200">
                                New Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                                <input
                                    id="new_password"
                                    name="new_password"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    value={formData.new_password}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2.5 border border-slate-700/50 rounded-lg placeholder-slate-500 text-white bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                    placeholder="Create a new password"
                                />
                            </div>
                            <p className="text-xs text-slate-500">At least 8 characters recommended</p>
                        </div>

                        {/* Confirm New Password */}
                        <div className="space-y-2">
                            <label htmlFor="confirm_password" className="block text-sm font-semibold text-slate-200">
                                Confirm New Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                                <input
                                    id="confirm_password"
                                    name="confirm_password"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    value={formData.confirm_password}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2.5 border border-slate-700/50 rounded-lg placeholder-slate-500 text-white bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                                    placeholder="Re-enter your new password"
                                />
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm flex items-start space-x-2">
                                <span className="text-lg">⚠️</span>
                                <span>{error}</span>
                            </div>
                        )}

                        {/* Password Requirements */}
                        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
                            <p className="text-xs font-semibold text-emerald-300 mb-2">Password Requirements:</p>
                            <ul className="text-xs text-emerald-400/80 space-y-1">
                                <li>✓ Minimum 8 characters</li>
                                <li>✓ Different from current password</li>
                                <li>✓ Confirmation must match</li>
                            </ul>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-sm font-semibold text-white bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg"
                        >
                            {isLoading ? (
                                <div className="flex items-center space-x-2">
                                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    <span>Updating password...</span>
                                </div>
                            ) : (
                                'Change Password'
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="text-center text-xs text-slate-500 border-t border-slate-700/50 pt-4">
                        <p>© 2026 CFO Chatbot. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
