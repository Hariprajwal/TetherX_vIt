// src/components/AdaptRolePanel.js
import React, { useState } from 'react';
import { aiAPI } from '../api/endpoints';

const FEATURES = [
    { key: 'threat_level', label: 'Threat Level', desc: '0 = safe, 1 = critical' },
    { key: 'time_normalized', label: 'Time of Day', desc: '0 = midnight, 0.5 = noon, 1 = midnight' },
    { key: 'location_risk', label: 'Location Risk', desc: '0 = secure zone, 1 = high-risk area' },
    { key: 'access_frequency', label: 'Access Frequency', desc: '0 = rare, 1 = burst' },
    { key: 'credential_strength', label: 'Credential Strength', desc: '0 = weak, 1 = strong' },
];

export default function AdaptRolePanel({ userRole }) {
    const [values, setValues] = useState([0.5, 0.5, 0.5, 0.5, 0.5]);
    const [userId, setUserId] = useState('engineer_01');
    const [currentRole, setCurrentRole] = useState('viewer');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const canUse = ['admin', 'municipal', 'engineer'].includes(userRole);

    const handleSlider = (i, val) => {
        const newVals = [...values];
        newVals[i] = parseFloat(val);
        setValues(newVals);
    };

    const handlePredict = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await aiAPI.adaptRole({
                context: values,
                user_identifier: userId,
                current_role: currentRole,
            });
            setResult(res.data);
        } catch (err) {
            setResult({ error: err.response?.status === 403 ? 'Permission denied: your role cannot use AI tools.' : (err.response?.data || 'Prediction failed') });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="panel">
            <h2>🤖 Adapt Role — AI Prediction (LSTM)</h2>
            <p className="panel-desc">
                {canUse
                    ? 'Adjust the 5 context features and let the LSTM model predict the optimal role.'
                    : '🔒 Your role (viewer) cannot use AI tools. Contact an Engineer or Admin.'}
            </p>

            {canUse && (
                <div className="ai-form">
                    <div className="form-row">
                        <input placeholder="User ID" value={userId} onChange={e => setUserId(e.target.value)} />
                        <select value={currentRole} onChange={e => setCurrentRole(e.target.value)}>
                            {['viewer', 'Engineer', 'Municipal', 'admin'].map(r => <option key={r}>{r}</option>)}
                        </select>
                    </div>

                    <div className="sliders">
                        {FEATURES.map((f, i) => (
                            <div key={f.key} className="slider-group">
                                <label>{f.label}: <strong>{values[i].toFixed(2)}</strong></label>
                                <input type="range" min="0" max="1" step="0.01" value={values[i]} onChange={e => handleSlider(i, e.target.value)} />
                                <span className="slider-desc">{f.desc}</span>
                            </div>
                        ))}
                    </div>

                    <button onClick={handlePredict} className="btn-ai" disabled={loading}>
                        {loading ? '⏳ Predicting...' : '🚀 Run AI Prediction'}
                    </button>
                </div>
            )}

            {result && (
                <div className={`ai-result ${result.error ? 'result-error' : 'result-success'}`}>
                    {result.error ? (
                        <pre>{typeof result.error === 'string' ? result.error : JSON.stringify(result.error, null, 2)}</pre>
                    ) : (
                        <>
                            <div className="result-main">
                                <span className="result-label">Recommended Role:</span>
                                <span className={`result-role role-${result.recommended_role}`}>{result.recommended_role}</span>
                            </div>
                            <div className="result-meta">
                                <span>Source: {result.from_edge ? '⚡ Edge Node' : '💻 Local Inference'}</span>
                                <span>Status: {result.edge_status}</span>
                                <span>Previous: {result.previous_role}</span>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
