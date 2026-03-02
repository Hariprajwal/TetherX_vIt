// src/components/AuditLogsPanel.js
import React, { useState, useEffect } from 'react';
import { auditLogsAPI } from '../api/endpoints';

export default function AuditLogsPanel({ userRole }) {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({ action: '', actor: '', details: '' });
    const [msg, setMsg] = useState({ text: '', type: '' });

    const canCreate = ['admin', 'municipal', 'engineer'].includes(userRole);

    const fetchLogs = () => {
        setLoading(true);
        auditLogsAPI.list()
            .then(res => setLogs(res.data))
            .catch(err => setMsg({ text: err.response?.status === 403 ? 'Access denied.' : 'Failed to load.', type: 'error' }))
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchLogs(); }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await auditLogsAPI.create(form);
            setMsg({ text: 'Audit log created with blockchain hash!', type: 'success' });
            setForm({ action: '', actor: '', details: '' });
            fetchLogs();
        } catch (err) {
            setMsg({ text: err.response?.status === 403 ? 'Permission denied.' : 'Create failed.', type: 'error' });
        }
    };

    return (
        <div className="panel">
            <h2>🔗 Audit Logs (Blockchain-Integrated)</h2>
            {msg.text && <div className={msg.type === 'success' ? 'panel-msg-success' : 'panel-msg-error'}>{msg.text}</div>}

            {canCreate && (
                <form onSubmit={handleCreate} className="panel-form">
                    <div className="form-row">
                        <input placeholder="Action (e.g., role_elevation)" value={form.action} onChange={e => setForm({ ...form, action: e.target.value })} required />
                        <input placeholder="Actor (e.g., mas_agent_01)" value={form.actor} onChange={e => setForm({ ...form, actor: e.target.value })} required />
                    </div>
                    <textarea placeholder="Details..." value={form.details} onChange={e => setForm({ ...form, details: e.target.value })} rows={2} />
                    <button type="submit" className="btn-create">+ Create Audit Entry</button>
                </form>
            )}

            {loading ? <p>Loading...</p> : (
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr><th>Block #</th><th>Action</th><th>Actor</th><th>Hash</th><th>Prev Hash</th><th>Verified</th><th>Time</th></tr>
                        </thead>
                        <tbody>
                            {logs.map(log => (
                                <tr key={log.id}>
                                    <td><span className="block-index">#{log.block_index}</span></td>
                                    <td>{log.action}</td>
                                    <td>{log.actor}</td>
                                    <td className="td-hash" title={log.block_hash}>{log.block_hash?.slice(0, 12)}...</td>
                                    <td className="td-hash" title={log.prev_hash}>{log.prev_hash?.slice(0, 12)}...</td>
                                    <td>{log.verified ? '✅' : '❌'}</td>
                                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {logs.length === 0 && <p className="empty-msg">No audit logs yet.</p>}
                </div>
            )}
        </div>
    );
}
