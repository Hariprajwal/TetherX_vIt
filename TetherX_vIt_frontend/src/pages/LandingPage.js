// src/pages/LandingPage.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png';
import slide1 from '../assets/image.png';
import slide2 from '../assets/image copy.png';
import slide3 from '../assets/image copy 2.png';

const SLIDES = [slide1, slide2, slide3];

export default function LandingPage() {
    const [currentSlide, setCurrentSlide] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentSlide((prev) => (prev + 1) % SLIDES.length);
        }, 4000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="landing">
            {/* ───── NAVBAR ───── */}
            <nav className="land-nav">
                <div className="land-nav-brand">
                    <img src={logo} alt="UrbanSecure" className="land-logo" />
                    <span className="land-nav-title">UrbanSecure</span>
                </div>
                <div className="land-nav-links">
                    <a href="#features">Features</a>
                    <a href="#architecture">Architecture</a>
                    <a href="#roles">Roles</a>
                    <a href="#tech">Tech Stack</a>
                    <Link to="/login" className="land-btn-nav">Sign In</Link>
                </div>
            </nav>

            {/* ───── HERO ───── */}
            <section className="land-hero">
                <div className="hero-bg-shapes">
                    <div className="shape shape-1"></div>
                    <div className="shape shape-2"></div>
                    <div className="shape shape-3"></div>
                    <div className="shape shape-grid"></div>
                </div>

                <div className="hero-split">
                    {/* Left — Text */}
                    <div className="hero-content">
                        <div className="hero-badge">🇮🇳 Made for India's Smart Cities</div>
                        <h1>Secure Access &amp; API Protection<br />for <span className="hero-highlight">Urban Systems</span></h1>
                        <p className="hero-sub">
                            AI-enhanced zero-trust security layer with blockchain-integrated audit trails,
                            LSTM-based role adaptation, and real-time anomaly detection — built to protect
                            India's critical city infrastructure.
                        </p>
                        <div className="hero-actions">
                            <Link to="/register" className="land-btn-primary">Get Started</Link>
                            <a href="#features" className="land-btn-secondary">Explore Features</a>
                        </div>
                        <div className="hero-stats">
                            <div className="stat-item"><span className="stat-num">4</span><span className="stat-label">Role Tiers</span></div>
                            <div className="stat-divider"></div>
                            <div className="stat-item"><span className="stat-num">SHA-256</span><span className="stat-label">Blockchain</span></div>
                            <div className="stat-divider"></div>
                            <div className="stat-item"><span className="stat-num">LSTM</span><span className="stat-label">AI Engine</span></div>
                            <div className="stat-divider"></div>
                            <div className="stat-item"><span className="stat-num">ABAC</span><span className="stat-label">Zero-Trust</span></div>
                        </div>
                    </div>

                    {/* Right — Auto-sliding Images */}
                    <div className="hero-slider">
                        <div className="slider-window">
                            {SLIDES.map((src, i) => (
                                <img
                                    key={i}
                                    src={src}
                                    alt={`Urban security slide ${i + 1}`}
                                    className={`slider-img ${i === currentSlide ? 'active' : ''}`}
                                />
                            ))}
                        </div>
                        <div className="slider-dots">
                            {SLIDES.map((_, i) => (
                                <button
                                    key={i}
                                    className={`slider-dot ${i === currentSlide ? 'active' : ''}`}
                                    onClick={() => setCurrentSlide(i)}
                                    aria-label={`Go to slide ${i + 1}`}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* ───── FEATURES ───── */}
            <section id="features" className="land-section">
                <div className="section-inner">
                    <h2 className="section-title">Core Capabilities</h2>
                    <p className="section-sub">Comprehensive security designed for India's urban infrastructure</p>
                    <div className="features-grid">
                        <div className="feature-card">
                            <div className="feature-icon">🔒</div>
                            <h3>ABAC Zero-Trust Policies</h3>
                            <p>Attribute-Based Access Control dynamically evaluates threat level, time, location, and credentials before granting access. No implicit trust — ever.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">🤖</div>
                            <h3>AI-Driven Role Adaptation</h3>
                            <p>LSTM neural network analyzes 5 real-time context features to predict and auto-adapt user roles. Supports edge computing via Flask micro-service.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">🔍</div>
                            <h3>Anomaly Detection</h3>
                            <p>Deep learning Autoencoder analyzes access patterns and flags anomalous behavior instantly using reconstruction error scoring.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">⛓️</div>
                            <h3>Blockchain Audit Trail</h3>
                            <p>Every security action is recorded as an immutable SHA-256 hash block. Tamper-proof verification ensures complete audit integrity.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">🛡️</div>
                            <h3>Multi-Agent System</h3>
                            <p>Autonomous agents monitor, evaluate, and enforce security policies in real-time without human intervention. Edge-deployable architecture.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">📊</div>
                            <h3>Access Monitoring</h3>
                            <p>Real-time dashboards track every API access with user identifiers, IP addresses, methods, anomaly scores, and role-based filtering.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ───── ARCHITECTURE ───── */}
            <section id="architecture" className="land-section land-section-alt">
                <div className="section-inner">
                    <h2 className="section-title">System Architecture</h2>
                    <p className="section-sub">How data flows through the zero-trust pipeline</p>
                    <div className="arch-flow">
                        <div className="arch-step">
                            <div className="arch-num">1</div>
                            <div className="arch-content">
                                <h4>API Request</h4>
                                <p>User sends request with JWT token via React frontend</p>
                            </div>
                        </div>
                        <div className="arch-arrow">→</div>
                        <div className="arch-step">
                            <div className="arch-num">2</div>
                            <div className="arch-content">
                                <h4>ABAC Middleware</h4>
                                <p>Zero-trust engine evaluates role, time, location &amp; threat</p>
                            </div>
                        </div>
                        <div className="arch-arrow">→</div>
                        <div className="arch-step">
                            <div className="arch-num">3</div>
                            <div className="arch-content">
                                <h4>AI Analysis</h4>
                                <p>LSTM predicts role, Autoencoder scores anomaly risk</p>
                            </div>
                        </div>
                        <div className="arch-arrow">→</div>
                        <div className="arch-step">
                            <div className="arch-num">4</div>
                            <div className="arch-content">
                                <h4>Blockchain Log</h4>
                                <p>Action hashed with SHA-256 into immutable audit chain</p>
                            </div>
                        </div>
                        <div className="arch-arrow">→</div>
                        <div className="arch-step">
                            <div className="arch-num">5</div>
                            <div className="arch-content">
                                <h4>Response</h4>
                                <p>Authorized data returned or access denied with log</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ───── ROLES ───── */}
            <section id="roles" className="land-section">
                <div className="section-inner">
                    <h2 className="section-title">Role Hierarchy</h2>
                    <p className="section-sub">Four-tier city operations access model</p>
                    <div className="roles-grid">
                        <div className="role-card role-admin">
                            <div className="role-tier">Tier 4 — Full Access</div>
                            <h3>Admin</h3>
                            <ul>
                                <li>Full CRUD on all resources</li>
                                <li>Create &amp; delete ABAC policies</li>
                                <li>Manage users and system config</li>
                                <li>Access all AI tools</li>
                            </ul>
                        </div>
                        <div className="role-card role-municipal">
                            <div className="role-tier">Tier 3 — Manage</div>
                            <h3>Municipal Officer</h3>
                            <ul>
                                <li>Read/write on all data</li>
                                <li>Create ABAC policies</li>
                                <li>Cannot delete system policies</li>
                                <li>Full AI tool access</li>
                            </ul>
                        </div>
                        <div className="role-card role-engineer">
                            <div className="role-tier">Tier 2 — Operate</div>
                            <h3>Engineer</h3>
                            <ul>
                                <li>Read access to logs</li>
                                <li>Create access &amp; audit entries</li>
                                <li>Use AI prediction tools</li>
                                <li>Cannot manage policies</li>
                            </ul>
                        </div>
                        <div className="role-card role-viewer-card">
                            <div className="role-tier">Tier 1 — View</div>
                            <h3>Viewer</h3>
                            <ul>
                                <li>Read own access logs only</li>
                                <li>Verify blockchain integrity</li>
                                <li>No AI tools or policy access</li>
                                <li>Cannot create or modify data</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* ───── TECH STACK ───── */}
            <section id="tech" className="land-section land-section-alt">
                <div className="section-inner">
                    <h2 className="section-title">Technology Stack</h2>
                    <p className="section-sub">Enterprise-grade technologies powering UrbanSecure</p>
                    <div className="tech-grid">
                        <div className="tech-group">
                            <h4>Backend</h4>
                            <div className="tech-tags">
                                <span className="tech-tag">Django 5.2</span>
                                <span className="tech-tag">Django REST Framework</span>
                                <span className="tech-tag">SimpleJWT</span>
                                <span className="tech-tag">SQLite / PostgreSQL</span>
                            </div>
                        </div>
                        <div className="tech-group">
                            <h4>Frontend</h4>
                            <div className="tech-tags">
                                <span className="tech-tag">React 19</span>
                                <span className="tech-tag">React Router v7</span>
                                <span className="tech-tag">Axios</span>
                                <span className="tech-tag">CSS3 Variables</span>
                            </div>
                        </div>
                        <div className="tech-group">
                            <h4>AI / ML</h4>
                            <div className="tech-tags">
                                <span className="tech-tag">PyTorch</span>
                                <span className="tech-tag">LSTM Network</span>
                                <span className="tech-tag">Autoencoder</span>
                                <span className="tech-tag">NumPy</span>
                            </div>
                        </div>
                        <div className="tech-group">
                            <h4>Security</h4>
                            <div className="tech-tags">
                                <span className="tech-tag">JWT Auth</span>
                                <span className="tech-tag">ABAC Zero-Trust</span>
                                <span className="tech-tag">SHA-256 Blockchain</span>
                                <span className="tech-tag">CORS</span>
                            </div>
                        </div>
                        <div className="tech-group">
                            <h4>Edge / MAS</h4>
                            <div className="tech-tags">
                                <span className="tech-tag">Flask Micro-service</span>
                                <span className="tech-tag">Multi-Agent System</span>
                                <span className="tech-tag">Edge Computing</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ───── CTA ───── */}
            <section className="land-cta">
                <div className="cta-inner">
                    <h2>Ready to Secure Your City?</h2>
                    <p>Create your account and start protecting urban infrastructure today.</p>
                    <div className="hero-actions">
                        <Link to="/register" className="land-btn-primary">Create Account</Link>
                        <Link to="/login" className="land-btn-secondary">Sign In</Link>
                    </div>
                </div>
            </section>

            {/* ───── FOOTER ───── */}
            <footer className="land-footer">
                <div className="footer-inner">
                    <div className="footer-brand">
                        <img src={logo} alt="UrbanSecure" className="footer-logo" />
                        <span>UrbanSecure AI-ZeroTrust</span>
                    </div>
                    <div className="footer-copy">
                        © 2026 UrbanSecure — Secure Access &amp; API Protection for Urban Systems
                    </div>
                    <div className="footer-flag">🇮🇳 Built for India's Smart Cities Mission</div>
                </div>
            </footer>
        </div>
    );
}
