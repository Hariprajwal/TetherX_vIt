// src/pages/LoginPage.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(username, password);
            navigate('/dashboard');
        } catch (err) {
            const data = err.response?.data;
            if (data?.needs_verification) {
                // Redirect to OTP verification page
                navigate('/verify', { state: { username: data.username || username } });
                return;
            }
            setError(data?.error || data?.detail || 'Login failed. Check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <img src={logo} alt="UrbanSecure" style={{ width: 48, height: 48, borderRadius: 8, marginBottom: 8 }} />
                    <h1>UrbanSecure AI</h1>
                    <p className="subtitle">Zero-Trust Security Portal</p>
                </div>
                <form onSubmit={handleSubmit} className="auth-form">
                    {error && <div className="error-msg">{error}</div>}
                    <div className="input-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                            autoFocus
                        />
                    </div>
                    <div className="input-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                            required
                        />
                    </div>
                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Authenticating...' : 'Sign In'}
                    </button>
                </form>
                <p className="auth-switch">
                    Don't have an account? <Link to="/register">Register</Link>
                </p>
                <p className="auth-switch" style={{ marginTop: '0.5rem' }}>
                    <Link to="/">← Back to Home</Link>
                </p>
            </div>
        </div>
    );
}
