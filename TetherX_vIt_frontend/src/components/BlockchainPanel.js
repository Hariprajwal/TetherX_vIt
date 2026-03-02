// src/components/BlockchainPanel.js
import React, { useState } from 'react';
import { aiAPI } from '../api/endpoints';

export default function BlockchainPanel() {
    const [chain, setChain] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleVerify = async () => {
        setLoading(true);
        try {
            const res = await aiAPI.verifyBlockchainPost();
            setChain(res.data);
        } catch (err) {
            setChain({ error: 'Verification failed' });
        } finally {
            setLoading(false);
        }
    };

    const handleLoad = async () => {
        setLoading(true);
        try {
            const res = await aiAPI.verifyBlockchain();
            setChain(res.data);
        } catch (err) {
            setChain({ error: 'Failed to load chain' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="panel">
            <h2>⛓️ Blockchain Audit Verification</h2>
            <p className="panel-desc">Verify the integrity of the tamper-proof SHA-256 hash chain.</p>

            <div className="btn-group">
                <button onClick={handleLoad} className="btn-ai" disabled={loading}>📋 Load Chain</button>
                <button onClick={handleVerify} className="btn-ai btn-verify" disabled={loading}>
                    {loading ? '⏳ Verifying...' : '🔐 Verify Integrity'}
                </button>
            </div>

            {chain && (
                <div className="blockchain-result">
                    {chain.error ? (
                        <div className="ai-result result-error"><pre>{chain.error}</pre></div>
                    ) : (
                        <>
                            <div className={`verify-banner ${chain.is_valid ? 'valid' : 'invalid'}`}>
                                <span className="verify-icon">{chain.is_valid ? '✅' : '❌'}</span>
                                <span>{chain.verification || (chain.is_valid ? 'CHAIN INTEGRITY: PASS' : 'TAMPERING DETECTED')}</span>
                                <span className="chain-length">Blocks: {chain.chain_length}</span>
                            </div>

                            {chain.chain && chain.chain.length > 0 && (
                                <div className="chain-blocks">
                                    {chain.chain.map((block, i) => (
                                        <div key={i} className="block-card">
                                            <div className="block-header">
                                                <span className="block-idx">Block #{block.index}</span>
                                                <span className="block-time">{block.timestamp}</span>
                                            </div>
                                            <div className="block-body">
                                                <div><strong>Data:</strong> {block.data}</div>
                                                <div className="block-hash"><strong>Hash:</strong> <code>{block.hash}</code></div>
                                                <div className="block-prev"><strong>Prev:</strong> <code>{block.prev_hash?.slice(0, 20)}...</code></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
