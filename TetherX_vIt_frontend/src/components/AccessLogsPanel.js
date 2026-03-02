// src/components/AccessLogsPanel.js
import React, { useState, useEffect } from 'react';
import { accessLogsAPI } from '../api/endpoints';

export default function AccessLogsPanel({ userRole }) {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({
        user_identifier: '', endpoint: '', method: 'GET', role: 'viewer',
        ip_address: '', anomaly_score: 0, is_anomalous: false, context_vector: '[]'
    });
    const [msg, setMsg] = useState({ text: '', type: '' });

    const canCreate = ['admin', 'municipal', 'engineer'].includes(userRole);
    const canDelete = ['admin', 'municipal'].includes(userRole);

    const fetchLogs = () => {
        setLoading(true);
        accessLogsAPI.list()
            .then(res => setLogs(res.data))
            .catch(err => setMsg({ text: err.response?.status === 403 ? 'Access denied for your role.' : 'Failed to load.', type: 'error' }))
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchLogs(); }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            let cv = [];
            try { cv = JSON.parse(form.context_vector); } catch { }
            await accessLogsAPI.create({ ...form, anomaly_score: parseFloat(form.anomaly_score), context_vector: cv });
            setMsg({ text: 'Access log created successfully!', type: 'success' });
            setForm({ user_identifier: '', endpoint: '', method: 'GET', role: 'viewer', ip_address: '', anomaly_score: 0, is_anomalous: false, context_vector: '[]' });
            fetchLogs();
        } catch (err) {
            setMsg({ text: err.response?.status === 403 ? 'Permission denied: your role cannot create logs.' : 'Create failed.', type: 'error' });
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Delete this log?')) return;
        try {
            await accessLogsAPI.delete(id);
            setMsg({ text: 'Log deleted successfully.', type: 'success' });
            fetchLogs();
        } catch (err) {
            setMsg({ text: err.response?.status === 403 ? 'Permission denied: your role cannot delete logs.' : 'Delete failed.', type: 'error' });
        }
    };

    return (
        <div className="panel">
            <h2>📊 Access Logs</h2>
            <p className="panel-desc">
                {userRole === 'viewer' ? 'Showing your access logs only.' : 'All system access logs.'}
            </p>
            {msg.text && <div className={msg.type === 'success' ? 'panel-msg-success' : 'panel-msg-error'}>{msg.text}</div>}

            {canCreate && (
                <form onSubmit={handleCreate} className="panel-form">
                    <div className="form-row">
                        <input placeholder="User identifier" value={form.user_identifier} onChange={e => setForm({ ...form, user_identifier: e.target.value })} required />
                        <input placeholder="Endpoint" value={form.endpoint} onChange={e => setForm({ ...form, endpoint: e.target.value })} required />
                        <select value={form.method} onChange={e => setForm({ ...form, method: e.target.value })}>
                            {['GET', 'POST', 'PUT', 'DELETE'].map(m => <option key={m}>{m}</option>)}
                        </select>
                    </div>
                    <div className="form-row">
                        <input placeholder="Role" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} />
                        <input placeholder="IP Address" value={form.ip_address} onChange={e => setForm({ ...form, ip_address: e.target.value })} />
                        <input type="number" step="0.01" placeholder="Anomaly score" value={form.anomaly_score} onChange={e => setForm({ ...form, anomaly_score: e.target.value })} />
                    </div>
                    <button type="submit" className="btn-create">+ Create Log</button>
                </form>
            )}

            {loading ? <p>Loading...</p> : (
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr><th>ID</th><th>User</th><th>Method</th><th>Endpoint</th><th>Role</th><th>IP</th><th>Anomaly</th><th>Time</th>{canDelete && <th>Actions</th>}</tr>
                        </thead>
                        <tbody>
                            {logs.map(log => (
                                <tr key={log.id} className={log.is_anomalous ? 'row-anomaly' : ''}>
                                    <td>{log.id}</td>
                                    <td>{log.user_identifier}</td>
                                    <td><span className={`method-badge method-${log.method}`}>{log.method}</span></td>
                                    <td className="td-endpoint">{log.endpoint}</td>
                                    <td>{log.role}</td>
                                    <td>{log.ip_address}</td>
                                    <td>{log.is_anomalous ? '⚠️ ' + log.anomaly_score : '✅ ' + log.anomaly_score}</td>
                                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                                    {canDelete && <td><button className="btn-delete" onClick={() => handleDelete(log.id)}>🗑</button></td>}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {logs.length === 0 && <p className="empty-msg">No access logs found.</p>}
                </div>
            )}
        </div>
    );
}
