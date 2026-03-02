// src/pages/VerifyPage.js
import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../api/endpoints';
import logo from '../assets/logo.png';

export default function VerifyPage() {
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const { verifyOTP } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const username = location.state?.username || '';

    const handleVerify = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);
        try {
            await verifyOTP(username, code);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.error || 'Verification failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setResending(true);
        setError('');
        setSuccess('');
        try {
            const res = await authAPI.resendOTP({ username });
            setSuccess(res.data.message || 'OTP resent!');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to resend OTP.');
        } finally {
            setResending(false);
        }
    };

    if (!username) {
        return (
            <div className="auth-page">
                <div className="auth-card">
                    <div className="auth-header">
                        <img src={logo} alt="UrbanSecure" style={{ width: 48, height: 48, borderRadius: 8, marginBottom: 8 }} />
                        <h1>Verification Required</h1>
                        <p className="subtitle">No username provided. Please register first.</p>
                    </div>
                    <Link to="/register" className="btn-primary" style={{ display: 'block', textAlign: 'center', textDecoration: 'none' }}>
                        Go to Register
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <img src={logo} alt="UrbanSecure" style={{ width: 48, height: 48, borderRadius: 8, marginBottom: 8 }} />
                    <h1>Verify Your Email</h1>
                    <p className="subtitle">
                        We sent a 6-digit OTP to your email.<br />
                        Enter it below to activate your account.
                    </p>
                </div>
                <form onSubmit={handleVerify} className="auth-form">
                    {error && <div className="error-msg">{error}</div>}
                    {success && <div className="success-msg">{success}</div>}
                    <div className="input-group">
                        <label>Username</label>
                        <input type="text" value={username} disabled />
                    </div>
                    <div className="input-group">
                        <label>Verification Code (OTP)</label>
                        <input
                            type="text"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            placeholder="Enter 6-digit OTP"
                            required
                            maxLength={6}
                            autoFocus
                            style={{ textAlign: 'center', fontSize: '1.3rem', letterSpacing: '0.3em' }}
                        />
                    </div>
                    <button type="submit" className="btn-primary" disabled={loading || code.length !== 6}>
                        {loading ? 'Verifying...' : 'Verify Account'}
                    </button>
                </form>
                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                    <button
                        onClick={handleResend}
                        disabled={resending}
                        style={{ background: 'none', border: 'none', color: 'var(--teal)', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}
                    >
                        {resending ? 'Resending...' : "Didn't receive it? Resend OTP"}
                    </button>
                </div>
                <p className="auth-switch" style={{ marginTop: '0.5rem' }}>
                    <Link to="/login">← Back to Login</Link>
                </p>
            </div>
        </div>
    );
}
