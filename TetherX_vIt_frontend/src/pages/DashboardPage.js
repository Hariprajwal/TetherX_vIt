// src/pages/DashboardPage.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AccessLogsPanel from '../components/AccessLogsPanel';
import AuditLogsPanel from '../components/AuditLogsPanel';
import ABACPoliciesPanel from '../components/ABACPoliciesPanel';
import RoleAdaptationsPanel from '../components/RoleAdaptationsPanel';
import AdaptRolePanel from '../components/AdaptRolePanel';
import AnomalyDetectPanel from '../components/AnomalyDetectPanel';
import BlockchainPanel from '../components/BlockchainPanel';
import SettingsPage from './SettingsPage';
import logo from '../assets/logo.png';

/*
  Role-based visibility:
    admin      → ALL tabs
    Municipal  → ALL tabs
    Engineer   → Access Logs, Audit Logs, Role History, Blockchain, AI Tools, Settings
    viewer     → Access Logs (own only), Blockchain (verify only), Settings
*/
const ROLE_PERMISSIONS = {
    admin: ['access', 'audit', 'roles', 'abac', 'blockchain', 'adapt', 'anomaly', 'settings'],
    municipal: ['access', 'audit', 'roles', 'abac', 'blockchain', 'adapt', 'anomaly', 'settings'],
    engineer: ['access', 'audit', 'roles', 'blockchain', 'adapt', 'anomaly', 'settings'],
    viewer: ['access', 'blockchain', 'settings'],
};

const ALL_SECTIONS = [
    {
        section: 'Monitoring',
        tabs: [
            { key: 'access', label: 'Access Logs', icon: '📊' },
            { key: 'audit', label: 'Audit Logs', icon: '🔗' },
            { key: 'roles', label: 'Role History', icon: '🔄' },
        ]
    },
    {
        section: 'Security',
        tabs: [
            { key: 'abac', label: 'ABAC Policies', icon: '🔒' },
            { key: 'blockchain', label: 'Blockchain', icon: '⛓️' },
        ]
    },
    {
        section: 'AI Tools',
        tabs: [
            { key: 'adapt', label: 'Adapt Role', icon: '🤖' },
            { key: 'anomaly', label: 'Anomaly Detect', icon: '🔍' },
        ]
    },
    {
        section: 'Account',
        tabs: [
            { key: 'settings', label: 'Settings', icon: '⚙️' },
        ]
    }
];

export default function DashboardPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('access');
    const [darkMode, setDarkMode] = useState(() => localStorage.getItem('theme') === 'dark');

    const userRole = (user?.role || 'viewer').toLowerCase();
    const allowedTabs = ROLE_PERMISSIONS[userRole] || ROLE_PERMISSIONS.viewer;

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
        localStorage.setItem('theme', darkMode ? 'dark' : 'light');
    }, [darkMode]);

    const handleLogout = () => { logout(); navigate('/login'); };

    // Filter sections to only show tabs the user has access to
    const visibleSections = ALL_SECTIONS
        .map(s => ({
            ...s,
            tabs: s.tabs.filter(t => allowedTabs.includes(t.key))
        }))
        .filter(s => s.tabs.length > 0);

    const renderPanel = () => {
        // Block access if tab not allowed
        if (!allowedTabs.includes(activeTab)) {
            return (
                <div className="panel">
                    <h2>🚫 Access Denied</h2>
                    <p className="panel-desc">Your role ({userRole}) does not have permission to access this section.</p>
                </div>
            );
        }
        switch (activeTab) {
            case 'access': return <AccessLogsPanel userRole={userRole} />;
            case 'audit': return <AuditLogsPanel userRole={userRole} />;
            case 'abac': return <ABACPoliciesPanel userRole={userRole} />;
            case 'roles': return <RoleAdaptationsPanel userRole={userRole} />;
            case 'adapt': return <AdaptRolePanel userRole={userRole} />;
            case 'anomaly': return <AnomalyDetectPanel userRole={userRole} />;
            case 'blockchain': return <BlockchainPanel userRole={userRole} />;
            case 'settings': return <SettingsPage />;
            default: return <AccessLogsPanel userRole={userRole} />;
        }
    };

    return (
        <div className="dashboard">
            <header className="dash-header">
                <div className="dash-brand">
                    <img src={logo} alt="UrbanSecure" style={{ width: 28, height: 28, borderRadius: 4 }} />
                    <h1>UrbanSecure AI-ZeroTrust</h1>
                </div>
                <div className="dash-user">
                    <span className="user-badge">{user?.role || 'viewer'}</span>
                    <span className="user-name">{user?.username}</span>
                    <button className="btn-theme" onClick={() => setDarkMode(!darkMode)} title={darkMode ? 'Light mode' : 'Dark mode'}>
                        {darkMode ? '☀️' : '🌙'}
                    </button>
                    <button onClick={handleLogout} className="btn-logout">Sign out</button>
                </div>
            </header>

            <div className="dash-body">
                <nav className="dash-sidebar">
                    {visibleSections.map(s => (
                        <React.Fragment key={s.section}>
                            <div className="sidebar-section">{s.section}</div>
                            {s.tabs.map(tab => (
                                <button
                                    key={tab.key}
                                    className={`sidebar-btn ${activeTab === tab.key ? 'active' : ''}`}
                                    onClick={() => setActiveTab(tab.key)}
                                >
                                    <span className="sidebar-icon">{tab.icon}</span>
                                    {tab.label}
                                </button>
                            ))}
                        </React.Fragment>
                    ))}
                </nav>

                <main className="dash-content">
                    {renderPanel()}
                </main>
            </div>
        </div>
    );
}
