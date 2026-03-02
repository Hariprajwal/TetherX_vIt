// src/components/RoleAdaptationsPanel.js
import React, { useState, useEffect } from 'react';
import { roleAdaptationsAPI } from '../api/endpoints';

export default function RoleAdaptationsPanel() {
    const [adaptations, setAdaptations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        roleAdaptationsAPI.list()
            .then(res => setAdaptations(res.data))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="panel">
            <h2>🔄 Role Adaptations (MAS History)</h2>
            <p className="panel-desc">AI-driven role changes recorded by the Multi-Agent System</p>

            {loading ? <p>Loading...</p> : (
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr><th>User</th><th>Old Role</th><th>→</th><th>New Role</th><th>Adapted By</th><th>Edge?</th><th>Reason</th><th>Time</th></tr>
                        </thead>
                        <tbody>
                            {adaptations.map(a => (
                                <tr key={a.id}>
                                    <td>{a.user_identifier}</td>
                                    <td><span className="role-badge old">{a.old_role}</span></td>
                                    <td>→</td>
                                    <td><span className="role-badge new">{a.new_role}</span></td>
                                    <td><span className={`source-badge source-${a.adapted_by}`}>{a.adapted_by}</span></td>
                                    <td>{a.from_edge ? '⚡ Yes' : 'No'}</td>
                                    <td className="td-reason">{a.reason}</td>
                                    <td>{new Date(a.timestamp).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            {!loading && adaptations.length === 0 && (
                <p className="empty-msg">No role adaptations yet. Use the "Adapt Role (AI)" tab to trigger one.</p>
            )}
        </div>
    );
}
