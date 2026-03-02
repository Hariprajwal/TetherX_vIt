// src/pages/RegisterPage.js
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../api/endpoints';
import logo from '../assets/logo.png';

const ROLES = ['viewer', 'Engineer', 'Municipal'];  // NO admin

function getPasswordStrength(pw) {
    let score = 0;
    if (pw.length >= 8) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[a-z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pw)) score++;
    if (score <= 1) return { level: 'weak', label: 'Weak' };
    if (score <= 2) return { level: 'fair', label: 'Fair' };
    if (score <= 3) return { level: 'good', label: 'Good' };
    return { level: 'strong', label: 'Strong' };
}

export default function RegisterPage() {
    const [form, setForm] = useState({ username: '', email: '', password: '', password_confirm: '', role: 'viewer' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [usernameStatus, setUsernameStatus] = useState(null);
    const [emailStatus, setEmailStatus] = useState(null);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const checkUsername = useCallback((username) => {
        if (username.length < 3) { setUsernameStatus(null); return; }
        const timer = setTimeout(() => {
            authAPI.checkUsername(username)
                .then(res => setUsernameStatus(res.data))
                .catch(() => setUsernameStatus(null));
        }, 400);
        return () => clearTimeout(timer);
    }, []);

    const checkEmail = useCallback((email) => {
        if (!email || !email.includes('@')) { setEmailStatus(null); return; }
        const timer = setTimeout(() => {
            authAPI.checkEmail(email)
                .then(res => setEmailStatus(res.data))
                .catch(() => setEmailStatus(null));
        }, 400);
        return () => clearTimeout(timer);
    }, []);

    useEffect(() => { const cleanup = checkUsername(form.username); return cleanup; }, [form.username, checkUsername]);
    useEffect(() => { const cleanup = checkEmail(form.email); return cleanup; }, [form.email, checkEmail]);

    const pwStrength = form.password ? getPasswordStrength(form.password) : null;
    const passwordsMatch = form.password_confirm && form.password === form.password_confirm;
    const passwordsMismatch = form.password_confirm && form.password !== form.password_confirm;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (usernameStatus && !usernameStatus.available) { setError('Username is already taken.'); return; }
        if (emailStatus && !emailStatus.available) { setError('Email is already registered.'); return; }
        if (form.password !== form.password_confirm) { setError('Passwords do not match.'); return; }
        setLoading(true);
        try {
            await register(form);
            // Redirect to OTP verification page (NOT dashboard)
            navigate('/verify', { state: { username: form.username } });
        } catch (err) {
            const data = err.response?.data;
            if (data) {
                const messages = [];
                Object.entries(data).forEach(([key, val]) => {
                    const msgs = Array.isArray(val) ? val : [val];
                    msgs.forEach(m => messages.push(typeof m === 'string' ? m : JSON.stringify(m)));
                });
                setError(messages.join(' '));
            } else {
                setError('Registration failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <img src={logo} alt="UrbanSecure" style={{ width: 48, height: 48, borderRadius: 8, marginBottom: 8 }} />
                    <h1>Create Account</h1>
                    <p className="subtitle">Join UrbanSecure AI-ZeroTrust</p>
                </div>
                <form onSubmit={handleSubmit} className="auth-form">
                    {error && <div className="error-msg">{error}</div>}

                    <div className="input-group">
                        <label>Username</label>
                        <input name="username" value={form.username} onChange={handleChange}
                            placeholder="Min 3 chars, letters/numbers/underscores" required minLength={3} autoFocus />
                        {usernameStatus && (
                            <span className={usernameStatus.available ? 'input-success-text' : 'input-error-text'}>
                                {usernameStatus.available ? '✓ ' : '✗ '}{usernameStatus.message}
                            </span>
                        )}
                    </div>

                    <div className="input-group">
                        <label>Email</label>
                        <input name="email" type="email" value={form.email} onChange={handleChange}
                            placeholder="your@email.com — OTP will be sent here" required />
                        {emailStatus && (
                            <span className={emailStatus.available ? 'input-success-text' : 'input-error-text'}>
                                {emailStatus.available ? '✓ ' : '✗ '}{emailStatus.message}
                            </span>
                        )}
                    </div>

                    <div className="input-group">
                        <label>Password</label>
                        <input name="password" type="password" value={form.password} onChange={handleChange}
                            placeholder="Min 8 chars with uppercase, lowercase, digit & special" required minLength={8} />
                        {pwStrength && (
                            <div className="password-strength">
                                <div className="strength-bar-track">
                                    <div className={`strength-bar-fill ${pwStrength.level}`}></div>
                                </div>
                                <div className={`strength-label ${pwStrength.level}`}>{pwStrength.label}</div>
                            </div>
                        )}
                    </div>

                    <div className="input-group">
                        <label>Confirm Password</label>
                        <input name="password_confirm" type="password" value={form.password_confirm} onChange={handleChange}
                            placeholder="Re-enter password" required minLength={8} />
                        {passwordsMatch && <span className="input-success-text">✓ Passwords match</span>}
                        {passwordsMismatch && <span className="input-error-text">✗ Passwords do not match</span>}
                    </div>

                    <div className="input-group">
                        <label>City Role</label>
                        <select name="role" value={form.role} onChange={handleChange}>
                            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                        </select>
                        <span className="input-hint">Your access level in the urban system</span>
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Creating Account...' : 'Register'}
                    </button>
                </form>
                <p className="auth-switch">
                    Already have an account? <Link to="/login">Sign In</Link>
                </p>
            </div>
        </div>
    );
}
