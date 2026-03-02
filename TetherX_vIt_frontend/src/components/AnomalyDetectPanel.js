// src/components/AnomalyDetectPanel.js
import React, { useState } from 'react';
import { aiAPI } from '../api/endpoints';

export default function AnomalyDetectPanel({ userRole }) {
    const [vectorStr, setVectorStr] = useState('0.95, 0.88, 0.1, 0.99, 0.05');
    const [userId, setUserId] = useState('sensor_42');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const canUse = ['admin', 'municipal', 'engineer'].includes(userRole);

    const handleDetect = async () => {
        setLoading(true);
        setResult(null);
        try {
            const vector = vectorStr.split(',').map(v => parseFloat(v.trim()));
            const res = await aiAPI.detectAnomaly({ input_vector: vector, user_identifier: userId });
            setResult(res.data);
        } catch (err) {
            setResult({ error: err.response?.status === 403 ? 'Permission denied: your role cannot use AI tools.' : (err.response?.data || 'Detection failed') });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="panel">
            <h2>🔍 Anomaly Detection — Deep Learning (Autoencoder)</h2>
            <p className="panel-desc">
                {canUse
                    ? 'Enter a feature vector to detect anomalous access patterns.'
                    : '🔒 Your role (viewer) cannot use AI tools. Contact an Engineer or Admin.'}
            </p>

            {canUse && (
                <div className="ai-form">
                    <div className="form-row">
                        <input placeholder="User/Sensor ID" value={userId} onChange={e => setUserId(e.target.value)} />
                    </div>
                    <div className="input-group">
                        <label>Input Vector (comma-separated floats)</label>
                        <input value={vectorStr} onChange={e => setVectorStr(e.target.value)} placeholder="0.95, 0.88, 0.1, 0.99, 0.05" />
                    </div>
                    <button onClick={handleDetect} className="btn-ai" disabled={loading}>
                        {loading ? '⏳ Analyzing...' : '🔬 Run Anomaly Detection'}
                    </button>
                </div>
            )}

            {result && (
                <div className={`ai-result ${result.error ? 'result-error' : result.is_anomalous ? 'result-anomaly' : 'result-success'}`}>
                    {result.error ? (
                        <pre>{typeof result.error === 'string' ? result.error : JSON.stringify(result.error, null, 2)}</pre>
                    ) : (
                        <>
                            <div className="result-main">
                                <span className="result-label">Status:</span>
                                <span className={result.is_anomalous ? 'anomaly-alert' : 'normal-status'}>
                                    {result.is_anomalous ? '⚠️ ANOMALY DETECTED' : '✅ NORMAL'}
                                </span>
                            </div>
                            <div className="result-meta">
                                <span>Anomaly Score: {result.anomaly_score}</span>
                                <span>Vector Length: {result.vector_length}</span>
                                <span>User: {result.user_identifier}</span>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
