// src/pages/SettingsPage.js
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../api/endpoints';
import { useNavigate } from 'react-router-dom';

export default function SettingsPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    // Password change state
    const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', new_password_confirm: '' });
    const [pwMsg, setPwMsg] = useState({ text: '', type: '' });
    const [pwLoading, setPwLoading] = useState(false);

    // Delete account state
    const [showDelete, setShowDelete] = useState(false);
    const [delForm, setDelForm] = useState({ password: '', confirmation: '' });
    const [delMsg, setDelMsg] = useState({ text: '', type: '' });
    const [delLoading, setDelLoading] = useState(false);

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        setPwMsg({ text: '', type: '' });
        setPwLoading(true);
        try {
            const res = await authAPI.changePassword(pwForm);
            setPwMsg({ text: res.data.message, type: 'success' });
            setPwForm({ current_password: '', new_password: '', new_password_confirm: '' });
        } catch (err) {
            const data = err.response?.data;
            const msg = data ? Object.values(data).flat().join(' ') : 'Password change failed.';
            setPwMsg({ text: msg, type: 'error' });
        } finally {
            setPwLoading(false);
        }
    };

    const handleDeleteAccount = async (e) => {
        e.preventDefault();
        setDelMsg({ text: '', type: '' });
        setDelLoading(true);
        try {
            await authAPI.deleteAccount(delForm);
            logout();
            navigate('/login');
        } catch (err) {
            const data = err.response?.data;
            const msg = data ? Object.values(data).flat().join(' ') : 'Deletion failed.';
            setDelMsg({ text: msg, type: 'error' });
        } finally {
            setDelLoading(false);
        }
    };

    return (
        <div className="panel settings-layout">
            <h2>⚙️ Settings</h2>
            <p className="panel-desc">Manage your account, security, and preferences.</p>

            {/* User Details */}
            <div className="settings-card">
                <h3>Account Information</h3>
                <div className="settings-row">
                    <span className="settings-label">Username</span>
                    <span className="settings-value">{user?.username}</span>
                </div>
                <div className="settings-row">
                    <span className="settings-label">Email</span>
                    <span className="settings-value">{user?.email}</span>
                </div>
                <div className="settings-row">
                    <span className="settings-label">Role</span>
                    <span className="settings-value">{user?.role || 'viewer'}</span>
                </div>
                <div className="settings-row">
                    <span className="settings-label">Member Since</span>
                    <span className="settings-value">{user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : '-'}</span>
                </div>
                <div className="settings-row">
                    <span className="settings-label">Last Login</span>
                    <span className="settings-value">{user?.last_login ? new Date(user.last_login).toLocaleString() : 'Current session'}</span>
                </div>
            </div>

            {/* Change Password */}
            <div className="settings-card">
                <h3>Change Password</h3>
                {pwMsg.text && <div className={`settings-msg ${pwMsg.type}`}>{pwMsg.text}</div>}
                <form onSubmit={handlePasswordChange} className="settings-form">
                    <div className="input-group">
                        <label>Current Password</label>
                        <input type="password" value={pwForm.current_password}
                            onChange={e => setPwForm({ ...pwForm, current_password: e.target.value })}
                            placeholder="Enter current password" required />
                    </div>
                    <div className="input-group">
                        <label>New Password</label>
                        <input type="password" value={pwForm.new_password}
                            onChange={e => setPwForm({ ...pwForm, new_password: e.target.value })}
                            placeholder="Min 8 chars, uppercase, lowercase, digit, special" required minLength={8} />
                    </div>
                    <div className="input-group">
                        <label>Confirm New Password</label>
                        <input type="password" value={pwForm.new_password_confirm}
                            onChange={e => setPwForm({ ...pwForm, new_password_confirm: e.target.value })}
                            placeholder="Re-enter new password" required />
                    </div>
                    <button type="submit" className="btn-settings" disabled={pwLoading}>
                        {pwLoading ? 'Changing...' : 'Update Password'}
                    </button>
                </form>
            </div>

            {/* Danger Zone */}
            <div className="danger-zone">
                <h3>🚨 Danger Zone</h3>
                <p>Permanently delete your account and all associated data. This action <strong>cannot be undone</strong>.</p>

                {!showDelete ? (
                    <button className="btn-danger" onClick={() => setShowDelete(true)}>
                        Delete My Account
                    </button>
                ) : (
                    <form onSubmit={handleDeleteAccount} className="danger-confirm">
                        {delMsg.text && <div className={`settings-msg ${delMsg.type}`}>{delMsg.text}</div>}
                        <div className="input-group">
                            <label>Confirm your password</label>
                            <input type="password" value={delForm.password}
                                onChange={e => setDelForm({ ...delForm, password: e.target.value })}
                                placeholder="Enter your password" required />
                        </div>
                        <div className="input-group">
                            <label>Type <strong>DELETE MY ACCOUNT</strong> to confirm</label>
                            <input type="text" value={delForm.confirmation}
                                onChange={e => setDelForm({ ...delForm, confirmation: e.target.value })}
                                placeholder="DELETE MY ACCOUNT" required />
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button type="submit" className="btn-danger" disabled={delLoading || delForm.confirmation !== 'DELETE MY ACCOUNT'}>
                                {delLoading ? 'Deleting...' : 'Permanently Delete'}
                            </button>
                            <button type="button" className="btn-settings" onClick={() => { setShowDelete(false); setDelForm({ password: '', confirmation: '' }); }}>
                                Cancel
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
