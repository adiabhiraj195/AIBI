import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginRequest, AuthState } from '../types';
import * as api from '../services/api';

interface AuthContextType extends AuthState {
    login: (credentials: LoginRequest) => Promise<void>;
    register: (credentials: api.RegisterRequest) => Promise<void>;
    logout: () => void;
    updateUser: (user: User) => void;
    changePassword: (passwords: api.ChangePasswordRequest) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [authState, setAuthState] = useState<AuthState>({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: true,
    });

    // Initialize auth state from localStorage on mount
    useEffect(() => {
        const token = api.getAuthToken();
        const user = api.getAuthUser();

        if (token && user) {
            setAuthState({
                user,
                accessToken: token,
                isAuthenticated: true,
                isLoading: false,
            });
        } else {
            setAuthState(prev => ({ ...prev, isLoading: false }));
        }
    }, []);

    const login = async (credentials: LoginRequest) => {
        try {
            const response = await api.login(credentials);

            setAuthState({
                user: response.user,
                accessToken: response.access_token,
                isAuthenticated: true,
                isLoading: false,
            });
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const register = async (credentials: api.RegisterRequest) => {
        try {
            const response = await api.register(credentials);

            if (!response.success) {
                throw new Error(response.message);
            }

            // After registration, user needs to login
            // Don't automatically log them in - redirect to login page
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    };

    const logout = () => {
        api.logout();
        setAuthState({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            isLoading: false,
        });
    };

    const updateUser = (user: User) => {
        api.setAuthUser(user);
        setAuthState(prev => ({ ...prev, user }));
    };

    const changePassword = async (passwords: api.ChangePasswordRequest) => {
        try {
            const response = await api.changePassword(passwords);

            if (!response.success) {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Change password failed:', error);
            throw error;
        }
    };

    return (
        <AuthContext.Provider value={{ ...authState, login, register, logout, updateUser, changePassword }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
