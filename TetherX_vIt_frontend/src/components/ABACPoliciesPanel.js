// src/components/ABACPoliciesPanel.js
import React, { useState, useEffect } from 'react';
import { abacPoliciesAPI } from '../api/endpoints';

export default function ABACPoliciesPanel({ userRole }) {
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({
        name: '', description: '', role: 'Engineer', attribute: 'time_of_day',
        condition: '', action: 'deny', is_active: true, priority: 10
    });
    const [msg, setMsg] = useState({ text: '', type: '' });

    const canCreate = ['admin', 'municipal'].includes(userRole);
    const canDelete = userRole === 'admin';

    const fetchPolicies = () => {
        setLoading(true);
        abacPoliciesAPI.list()
            .then(res => setPolicies(res.data))
            .catch(err => setMsg({ text: err.response?.status === 403 ? 'Access denied.' : 'Failed to load.', type: 'error' }))
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchPolicies(); }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await abacPoliciesAPI.create({ ...form, priority: parseInt(form.priority) });
            setMsg({ text: 'Policy created successfully!', type: 'success' });
            setForm({ name: '', description: '', role: 'Engineer', attribute: 'time_of_day', condition: '', action: 'deny', is_active: true, priority: 10 });
            fetchPolicies();
        } catch (err) {
            setMsg({ text: err.response?.status === 403 ? 'Permission denied: only Admin/Municipal can create policies.' : 'Create failed.', type: 'error' });
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Delete this policy?')) return;
        try {
            await abacPoliciesAPI.delete(id);
            setMsg({ text: 'Policy deleted.', type: 'success' });
            fetchPolicies();
        } catch (err) {
            setMsg({ text: err.response?.status === 403 ? 'Permission denied: only Admin can delete policies.' : 'Delete failed.', type: 'error' });
        }
    };

    const toggleActive = async (policy) => {
        if (!canCreate) { setMsg({ text: 'Permission denied: your role cannot modify policies.', type: 'error' }); return; }
        await abacPoliciesAPI.patch(policy.id, { is_active: !policy.is_active });
        fetchPolicies();
    };

    return (
        <div className="panel">
            <h2>🔒 ABAC Zero-Trust Policies</h2>
            <p className="panel-desc">
                {canCreate ? 'Manage access control policies.' : 'View-only access. Contact an Admin to modify policies.'}
            </p>
            {msg.text && <div className={msg.type === 'success' ? 'panel-msg-success' : 'panel-msg-error'}>{msg.text}</div>}

            {canCreate && (
                <form onSubmit={handleCreate} className="panel-form">
                    <div className="form-row">
                        <input placeholder="Policy name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
                        <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
                            {['viewer', 'Engineer', 'Municipal', 'admin'].map(r => <option key={r}>{r}</option>)}
                        </select>
                        <select value={form.action} onChange={e => setForm({ ...form, action: e.target.value })}>
                            {['allow', 'deny', 'elevate', 'downgrade'].map(a => <option key={a}>{a}</option>)}
                        </select>
                    </div>
                    <div className="form-row">
                        <input placeholder="Attribute (e.g., time_of_day)" value={form.attribute} onChange={e => setForm({ ...form, attribute: e.target.value })} required />
                        <input placeholder="Condition (e.g., >= 20)" value={form.condition} onChange={e => setForm({ ...form, condition: e.target.value })} required />
                        <input type="number" placeholder="Priority" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })} />
                    </div>
                    <textarea placeholder="Description..." value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} />
                    <button type="submit" className="btn-create">+ Create Policy</button>
                </form>
            )}

            {loading ? <p>Loading...</p> : (
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr><th>Priority</th><th>Name</th><th>Role</th><th>Attribute</th><th>Condition</th><th>Action</th><th>Active</th>{canDelete && <th>Delete</th>}</tr>
                        </thead>
                        <tbody>
                            {policies.map(p => (
                                <tr key={p.id} className={!p.is_active ? 'row-inactive' : ''}>
                                    <td><span className="priority-badge">{p.priority}</span></td>
                                    <td><strong>{p.name}</strong></td>
                                    <td>{p.role}</td>
                                    <td>{p.attribute}</td>
                                    <td><code>{p.condition}</code></td>
                                    <td><span className={`action-badge action-${p.action}`}>{p.action}</span></td>
                                    <td>
                                        <button className="btn-toggle" onClick={() => toggleActive(p)} disabled={!canCreate}>
                                            {p.is_active ? '✅ Active' : '❌ Inactive'}
                                        </button>
                                    </td>
                                    {canDelete && <td><button className="btn-delete" onClick={() => handleDelete(p.id)}>🗑</button></td>}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {policies.length === 0 && <p className="empty-msg">No ABAC policies configured.</p>}
                </div>
            )}
        </div>
    );
}
