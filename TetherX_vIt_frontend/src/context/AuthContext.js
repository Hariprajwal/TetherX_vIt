// src/context/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/endpoints';

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [tokens, setTokens] = useState(() => {
        const saved = localStorage.getItem('tokens');
        return saved ? JSON.parse(saved) : null;
    });
    const [loading, setLoading] = useState(true);

    // Restore user from tokens on mount ONLY
    useEffect(() => {
        const stored = localStorage.getItem('tokens');
        if (stored) {
            const parsed = JSON.parse(stored);
            if (parsed?.access) {
                authAPI.me()
                    .then(res => { setUser(res.data); setTokens(parsed); })
                    .catch(() => { setTokens(null); setUser(null); localStorage.removeItem('tokens'); })
                    .finally(() => setLoading(false));
            } else {
                setLoading(false);
            }
        } else {
            setLoading(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const login = async (username, password) => {
        const res = await authAPI.login({ username, password });
        const data = res.data;
        // Check if needs verification
        if (res.status === 403 || data.needs_verification) {
            const err = new Error('Account not verified');
            err.response = res;
            throw err;
        }
        const newTokens = { access: data.access, refresh: data.refresh };
        localStorage.setItem('tokens', JSON.stringify(newTokens));
        setTokens(newTokens);
        setUser(data.user);
        return data;
    };

    const register = async (formData) => {
        const res = await authAPI.register(formData);
        return res.data;
    };

    const verifyOTP = async (username, code) => {
        const res = await authAPI.verify({ username, verification_code: code });
        const data = res.data;
        if (data.access) {
            const newTokens = { access: data.access, refresh: data.refresh };
            localStorage.setItem('tokens', JSON.stringify(newTokens));
            setTokens(newTokens);
            setUser(data.user);
        }
        return data;
    };

    const logout = () => {
        setUser(null);
        setTokens(null);
        localStorage.removeItem('tokens');
    };

    const isAuthenticated = !!user && !!tokens?.access;

    return (
        <AuthContext.Provider value={{ user, tokens, loading, isAuthenticated, login, register, verifyOTP, logout }}>
            {children}
        </AuthContext.Provider>
    );
}
