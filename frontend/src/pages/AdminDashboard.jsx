import { useEffect, useMemo, useRef, useState } from 'react';
import { adminAPI } from '../api/client';
import { useAuth } from '../context/AuthContext';
import ModelManager from '../components/admin/ModelManager';
import AlertDetailPanel from '../components/admin/AlertDetailPanel';

function StatCard({ label, value, hint, accent }) {
  return (
    <div className="admin-stat-card" style={{ '--accent': accent }}>
      <div className="admin-stat-label">{label}</div>
      <div className="admin-stat-value">{value}</div>
      <div className="admin-stat-hint">{hint}</div>
    </div>
  );
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('new');
  const [searchTerm, setSearchTerm] = useState('');
  const [userSegment, setUserSegment] = useState('all');
  const [noteById, setNoteById] = useState({});
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [error, setError] = useState('');
  const [scoring, setScoring] = useState(false);

  const [activeSection, setActiveSection] = useState('overview');
  const sectionRefs = {
    overview: useRef(null),
    analytics: useRef(null),
    live: useRef(null),
    users: useRef(null),
    model: useRef(null),
  };

  useEffect(() => {
    document.body.classList.add('admin-page');
    return () => {
      document.body.classList.remove('admin-page');
    };
  }, []);


  const loadData = async (nextStatus = statusFilter) => {
    setLoading(true);
    setError('');
    try {
      const alertQuery = nextStatus && nextStatus !== 'all' ? { status: nextStatus } : {};
      const [statsData, alertsData] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getAlerts(alertQuery),
      ]);
      setStats(statsData.stats);
      setAlerts(alertsData.alerts || []);
    } catch (err) {
      setError(err?.data?.errors?.[0] || 'Failed to load admin dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(statusFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const statusFilters = useMemo(() => ([
    { key: 'all', label: 'All', count: stats?.total_alerts ?? alerts.length },
    { key: 'new', label: 'New', count: stats?.new_alerts ?? alerts.filter((item) => item.status === 'new').length },
    { key: 'acknowledged', label: 'Acknowledged', count: stats?.acknowledged_alerts ?? alerts.filter((item) => item.status === 'acknowledged').length },
    { key: 'in_review', label: 'In review', count: stats?.in_review_alerts ?? alerts.filter((item) => item.status === 'in_review').length },
    { key: 'resolved', label: 'Resolved', count: stats?.resolved_alerts ?? alerts.filter((item) => item.status === 'resolved').length },
  ]), [alerts, stats]);

  const currentStatusLabel = statusFilters.find((item) => item.key === statusFilter)?.label || 'New';
  const selectedAlert = selectedDetail?.alert || null;
  const scrollToSection = (section) => {
    window.setTimeout(() => {
      sectionRefs[section]?.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 0);
  };

  const navigateSection = (section, options = {}) => {
    setActiveSection(section);
    if (options.status !== undefined) {
      setStatusFilter(options.status);
    }
    if (options.userSegment !== undefined) {
      setUserSegment(options.userSegment);
    }
    if (options.search !== undefined) {
      setSearchTerm(options.search);
    }
    scrollToSection(section);
  };

  const filteredAlerts = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) return alerts;
    return alerts.filter((alert) => {
      const username = alert.user?.display_name || alert.user?.username || '';
      const haystack = [username, alert.user?.email, alert.reason, alert.status, String(alert.score), String(alert.severity)]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(term);
    });
  }, [alerts, searchTerm]);

  const visibleAlerts = filteredAlerts;

  const visibleUsers = useMemo(() => {
    const byUser = new Map();
    visibleAlerts.forEach((alert) => {
      const key = alert.user?.id ?? alert.user?.username ?? alert.user?.email ?? 'u';
      const current = byUser.get(key) || { user: alert.user, items: [] };
      current.items.push(alert);
      byUser.set(key, current);
    });
    return Array.from(byUser.values());
  }, [visibleAlerts]);

  const userRows = useMemo(() => {
    const rows = visibleUsers.map((entry) => {
      const maxSev = Math.max(...entry.items.map((item) => item.severity));
      const avgScore = entry.items.reduce((sum, item) => sum + Number(item.score || 0), 0) / Math.max(1, entry.items.length);
      return {
        ...entry,
        maxSev,
        avgScore,
        segment: entry.items.length >= 2 ? 'active' : maxSev >= 4 ? 'high-risk' : 'all',
      };
    });

    if (userSegment === 'active') {
      return rows.filter((row) => row.items.length >= 2);
    }
    if (userSegment === 'blocked') {
      return rows.filter((row) => row.maxSev >= 4);
    }
    return rows;
  }, [userSegment, visibleUsers]);

  const userSegmentLabel = userSegment === 'active' ? 'Active users' : userSegment === 'blocked' ? 'High-risk users' : 'All users';

  const topAlert = visibleAlerts[0] || alerts[0] || null;

  const totalHighSeverity = useMemo(() => alerts.filter((item) => item.severity >= 4).length, [alerts]);

  const handleAcknowledge = async (alertId) => {
    const note = noteById[alertId] || 'Acknowledged from dashboard';
    await adminAPI.acknowledge(alertId, note);
    setNoteById((prev) => ({ ...prev, [alertId]: '' }));
    await loadData();
  };

  const handleResolve = async (alertId) => {
    const note = noteById[alertId] || 'Resolved from dashboard';
    await adminAPI.resolve(alertId, note, 'resolved');
    setNoteById((prev) => ({ ...prev, [alertId]: '' }));
    await loadData();
  };

  const openDetail = async (alertId) => {
    try {
      const detail = await adminAPI.getAlert(alertId);
      setSelectedDetail(detail);
      setActiveSection('live');
    } catch (err) {
      setError('Failed to load alert details');
    }
  };

  const closeDetail = () => setSelectedDetail(null);

  const handleDetailAction = async () => {
    await loadData();
    closeDetail();
  };

  const handleScore = async () => {
    setScoring(true);
    setError('');
    try {
      await adminAPI.score({ threshold: 0.8 });
      await loadData();
    } catch (err) {
      setError(err?.data?.errors?.[0] || 'Scoring failed. Make sure model artifacts and features exist.');
    } finally {
      setScoring(false);
    }
  };

  const handleNotificationClick = () => {
    if (topAlert) {
      openDetail(topAlert.id);
      setActiveSection('live');
      scrollToSection('live');
      return;
    }
    navigateSection('live');
  };

  if (!user?.is_admin) {
    return (
      <div className="admin-dashboard-shell">
        <div className="admin-hero">
          <div className="admin-kicker">MindBloom Admin</div>
          <h1>Access restricted</h1>
          <p>Only admin users can open the anomaly monitoring dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-shell">
      <div className="mb-root admin-root">
        {/* SIDEBAR */}
        <aside className="mb-sidebar">
          <div className="mb-logo">
            <div className="mb-logo-icon">🌸</div>
            <div>
              <div className="mb-logo-text">MindBloom</div>
              <div className="mb-logo-sub">Admin</div>
            </div>
          </div>

          <div className="mb-nav-group">
            <div className="mb-nav-label">Dashboard</div>
            <button
              type="button"
              className={`mb-nav-item ${activeSection === 'overview' ? 'active' : ''}`}
              onClick={() => navigateSection('overview')}
            >
              <span style={{ fontSize: 14 }}>📌</span> Overview
            </button>
            <button
              type="button"
              className={`mb-nav-item ${activeSection === 'analytics' ? 'active' : ''}`}
              onClick={() => navigateSection('analytics')}
            >
              <span style={{ fontSize: 14 }}>📈</span> Analytics
            </button>
            <button
              type="button"
              className={`mb-nav-item ${activeSection === 'live' ? 'active' : ''}`}
              onClick={() => navigateSection('live')}
            >
              <span style={{ fontSize: 14 }}>🟣</span> Live Activity <span className="mb-badge">{alerts.length}</span>
            </button>
          </div>

          <div className="mb-nav-group">
            <div className="mb-nav-label">Users</div>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('users', { userSegment: 'all' })}>
              <span style={{ fontSize: 14 }}>👥</span> All Users
            </button>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('users', { userSegment: 'active' })}>
              <span style={{ fontSize: 14 }}>🧭</span> Active Users
            </button>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('users', { userSegment: 'blocked' })}>
              <span style={{ fontSize: 14 }}>⛔</span> Blocked
            </button>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('analytics')}>
              <span style={{ fontSize: 14 }}>⚑</span> Reports <span className="mb-badge warn">{stats?.new_alerts ?? alerts.length}</span>
            </button>
          </div>

          <div className="mb-nav-group">
            <div className="mb-nav-label">Tests & Growth</div>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('model')}>
              <span style={{ fontSize: 14 }}>🧠</span> Personality Tests
            </button>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('model')}>
              <span style={{ fontSize: 14 }}>📊</span> Growth Reports
            </button>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('model')}>
              <span style={{ fontSize: 14 }}>✅</span> Daily Tasks
            </button>
          </div>

          <div className="mb-nav-group">
            <div className="mb-nav-label">System</div>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('model')}>
              <span style={{ fontSize: 14 }}>⚙️</span> Model Manager
            </button>
            <button type="button" className="mb-nav-item" onClick={() => navigateSection('analytics')}>
              <span style={{ fontSize: 14 }}>🛡️</span> Security
            </button>
          </div>
        </aside>

        {/* MAIN */}
        <main className="mb-main">
          {/* TOPBAR */}
          <div className="mb-topbar">
            <div>
              <div className="mb-topbar-title">Dashboard Overview</div>
              <div className="mb-topbar-sub">Review anomaly alerts and model status</div>
            </div>

            <div className="mb-search admin-search-shell" title="Search alerts by user, reason, or status">
              <span style={{ fontSize: 14 }}>🔎</span>
              <input
                className="admin-search-input"
                type="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search alerts, users, status..."
                aria-label="Search alerts"
              />
              {searchTerm && (
                <button type="button" className="admin-search-clear" onClick={() => setSearchTerm('')} aria-label="Clear search">
                  ✕
                </button>
              )}
            </div>

            <div className="mb-topbar-actions">
              <button type="button" className="mb-icon-btn" aria-label="Open latest alert" onClick={handleNotificationClick}>
                <span style={{ fontSize: 16 }}>🔔</span>
                <div className="mb-notif-dot" />
              </button>
              <button type="button" className="mb-icon-btn" aria-label="Run scoring" onClick={handleScore} disabled={scoring} style={{ opacity: scoring ? 0.7 : 1 }}>
                <span style={{ fontSize: 16 }}>{scoring ? '⏳' : '▶'}</span>
              </button>
              <div className="mb-avatar" aria-label="Admin avatar">A</div>
            </div>
          </div>

          {/* CONTENT */}
          <div className="mb-content">
            {/* HERO */}
            <div className="mb-hero" ref={sectionRefs.overview}>
              <div className="mb-hero-text">
                <div className="mb-hero-greeting">Welcome back</div>
                <div className="mb-hero-title">MindBloom Admin Dashboard 🌸</div>
                <div className="mb-hero-sub">Anomaly detection control center</div>
                <div className="mb-hero-stats" style={{ marginTop: 12, gap: 18 }}>
                  <div className="mb-hero-stat">
                    <div className="mb-hero-stat-val">{stats?.new_alerts ?? alerts.length}</div>
                    <div className="mb-hero-stat-lbl">New alerts</div>
                  </div>
                  <div className="mb-hero-stat">
                    <div className="mb-hero-stat-val">{stats?.high_severity_alerts ?? totalHighSeverity}</div>
                    <div className="mb-hero-stat-lbl">High severity</div>
                  </div>
                  <div className="mb-hero-stat">
                    <div className="mb-hero-stat-val">{stats?.resolved_alerts ?? 0}</div>
                    <div className="mb-hero-stat-lbl">Resolved</div>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'flex-end', zIndex: 1 }}>
                <button className="admin-button primary" onClick={handleScore} disabled={scoring}>
                  {scoring ? 'Scoring...' : 'Run Scoring'}
                </button>
                <button type="button" className="admin-button ghost" onClick={() => loadData(statusFilter)}>
                  Refresh
                </button>
              </div>
            </div>

            <div className="admin-status-strip">
              <div className="admin-status-info">
                <div className="admin-status-label">Alert queue</div>
                <div className="admin-status-title">Viewing {currentStatusLabel.toLowerCase()} alerts</div>
              </div>
              <div className="admin-status-chips">
                {statusFilters.map((item) => (
                  <button
                    key={item.key}
                    type="button"
                    className={`admin-status-chip ${statusFilter === item.key ? 'active' : ''}`}
                    onClick={() => setStatusFilter(item.key)}
                  >
                    <span>{item.label}</span>
                    <strong>{item.count}</strong>
                  </button>
                ))}
              </div>
            </div>

            {error && <div className="admin-alert-banner">{error}</div>}

            {/* KPI CARDS */}
            <section className="mb-kpi-grid">
              <div className="mb-kpi-card">
                <div className="mb-kpi-icon" style={{ background: 'rgba(124,108,255,0.12)', color: '#7c6cff' }}>👥</div>
                <div className="mb-kpi-val">{stats?.total_alerts ?? 0}</div>
                <div className="mb-kpi-lbl">Total Alerts</div>
                <div className={`mb-kpi-trend mb-trend-up`}><span aria-hidden>↑</span> Model history</div>
              </div>
              <div className="mb-kpi-card">
                <div className="mb-kpi-icon" style={{ background: 'rgba(255,107,157,0.10)', color: '#ff6b9d' }}>🟣</div>
                <div className="mb-kpi-val">{stats?.new_alerts ?? alerts.length}</div>
                <div className="mb-kpi-lbl">New Alerts</div>
                <div className="mb-kpi-trend mb-trend-up"><span aria-hidden>↗</span> Awaiting review</div>
              </div>
              <div className="mb-kpi-card">
                <div className="mb-kpi-icon" style={{ background: 'rgba(245,158,11,0.10)', color: '#f59e0b' }}>⚠️</div>
                <div className="mb-kpi-val">{stats?.high_severity_alerts ?? totalHighSeverity}</div>
                <div className="mb-kpi-lbl">High Severity</div>
                <div className="mb-kpi-trend mb-trend-dn"><span aria-hidden>↓</span> Focus queue</div>
              </div>
              <div className="mb-kpi-card">
                <div className="mb-kpi-icon" style={{ background: 'rgba(46,204,113,0.10)', color: '#2ecc71' }}>✅</div>
                <div className="mb-kpi-val">{stats?.resolved_alerts ?? 0}</div>
                <div className="mb-kpi-lbl">Resolved</div>
                <div className="mb-kpi-trend mb-trend-up"><span aria-hidden>✓</span> Closed cases</div>
              </div>
            </section>

            {/* LOWER GRID */}
            <section className="mb-chart-row">
              {/* LEFT: model signal view */}
              <div className="mb-chart-card">
                <div className="mb-section-hd">
                  <div className="mb-section-title">Model signal landscape</div>
                  <div className="mb-section-pill">From recent alerts</div>
                </div>

                {(() => {
                  const total = Math.max(1, alerts.length);
                  const high = alerts.filter((a) => a.severity >= 4).length;
                  const med = alerts.filter((a) => a.severity === 3).length;
                  const low = alerts.filter((a) => a.severity <= 2).length;
                  const pct = (n) => Math.round((n / total) * 100);

                  const m1 = pct(high);
                  const m2 = pct(med);
                  const m3 = pct(low);
                  const p4 = Math.max(0, 100 - (m1 + m2 + m3));

                  return (
                    <>
                      <div className="mb-mood-row">
                        <div className="mb-mood-emo">⚠️ High</div>
                        <div className="mb-mood-track"><div className="mb-mood-fill" style={{ width: `${m1}%`, background: 'linear-gradient(90deg,#ef4444,#fca5a5)' }} /></div>
                        <div className="mb-mood-pct">{m1}%</div>
                      </div>
                      <div className="mb-mood-row">
                        <div className="mb-mood-emo">🟠 Medium</div>
                        <div className="mb-mood-track"><div className="mb-mood-fill" style={{ width: `${m2}%`, background: 'linear-gradient(90deg,#f59e0b,#fcd34d)' }} /></div>
                        <div className="mb-mood-pct">{m2}%</div>
                      </div>
                      <div className="mb-mood-row">
                        <div className="mb-mood-emo">🟢 Low</div>
                        <div className="mb-mood-track"><div className="mb-mood-fill" style={{ width: `${m3}%`, background: 'linear-gradient(90deg,#22c55e,#4ade80)' }} /></div>
                        <div className="mb-mood-pct">{m3}%</div>
                      </div>
                      <div className="mb-mood-row" style={{ opacity: 0.9 }}>
                        <div className="mb-mood-emo">📌 Review</div>
                        <div className="mb-mood-track"><div className="mb-mood-fill" style={{ width: `${p4}%`, background: 'linear-gradient(90deg,#7c6cff,#c084fc)' }} /></div>
                        <div className="mb-mood-pct">{p4}%</div>
                      </div>

                      <div style={{ marginTop: 14, borderTop: '1px solid rgba(124,108,255,0.08)', paddingTop: 12 }}>
                        <div style={{ fontSize: 10, color: '#8882b0', marginBottom: 10, fontStyle: 'italic' }}>
                          Higher score/severity means behavior deviates from user’s recent pattern.
                        </div>
                        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                          <button type="button" className="mb-section-pill-button" onClick={() => navigateSection('live')}>Acknowledge</button>
                          <button type="button" className="mb-section-pill-button danger" onClick={() => navigateSection('live')}>Resolve</button>
                          <button type="button" className="mb-section-pill-button accent" onClick={() => navigateSection('analytics')}>Review queue</button>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>

              {/* RIGHT: risk alerts + recent users table */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div className="mb-chart-card" style={{ padding: '14px 16px' }} ref={sectionRefs.users}>
                  <div className="mb-section-hd">
                    <div className="mb-section-title">⚠ Users needing attention</div>
                    <div className="mb-section-pill">{alerts.filter((a) => a.severity >= 4).length} flagged</div>
                  </div>

                  {loading ? (
                    <div className="admin-empty-state">Loading alerts...</div>
                  ) : visibleUsers.length === 0 ? (
                    <div className="admin-empty-state">No new alerts right now.</div>
                  ) : (
                    visibleAlerts.slice(0, 3).map((alert) => (
                      <div className="mb-alert" key={alert.id}>
                        <div className="mb-alert-icon">{alert.severity >= 4 ? '🚩' : '📝'}</div>
                        <div>
                          <div className="mb-alert-title">
                            {(alert.user?.display_name || alert.user?.username || 'User')} — {Number(alert.score).toFixed(2)}
                          </div>
                          <div className="mb-alert-sub">{alert.reason || 'Review required'}</div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="mb-chart-card" style={{ padding: '14px 16px' }}>
                  <div className="mb-section-hd">
                    <div className="mb-section-title">Recent users</div>
                    <button type="button" className="mb-section-pill mb-section-pill-button" style={{ cursor: 'pointer' }} onClick={() => navigateSection('users', { userSegment: 'all' })}>
                      View all
                    </button>
                  </div>

                  <div className="admin-user-segment-label">{userSegmentLabel}</div>

                  <table className="mb-user-table" aria-label="Recent users table">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Score</th>
                        <th>Alerts</th>
                        <th>Risk</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        const rows = userRows.slice(0, 4);
                        if (rows.length === 0) return null;
                        return rows.map(({ user, items, maxSev, avgScore }) => {
                          const label = maxSev >= 4 ? 'High' : maxSev === 3 ? 'Medium' : 'Low';
                          const cls = maxSev >= 4 ? 'mb-risk-hi' : maxSev === 3 ? 'mb-risk-med' : 'mb-risk-low';
                          return (
                            <tr key={(user?.id || user?.username || user?.email || 'u') + maxSev}>
                              <td>
                                <div className="mb-user-name-row">
                                  <div className="mb-user-ava" style={{ background: 'linear-gradient(135deg,#7c6cff,#c084fc)' }}>
                                    {(user?.display_name || user?.username || 'U').slice(0, 2).toUpperCase()}
                                  </div>
                                  <span style={{ fontSize: 12, fontWeight: 700 }}>{user?.display_name || user?.username}</span>
                                </div>
                              </td>
                              <td><span style={{ fontSize: 12, color: '#8882b0', fontWeight: 700 }}>{avgScore.toFixed(2)}</span></td>
                              <td><span style={{ fontSize: 12, color: '#8882b0', fontWeight: 700 }}>{items.length}</span></td>
                              <td><span className={`mb-risk-pill ${cls}`}>{label}</span></td>
                            </tr>
                          );
                        });
                      })()}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            {/* LIVE ALERTS TABLE */}
            <section className="mb-chart-card" style={{ marginBottom: 14 }} ref={sectionRefs.live}>
              <div className="mb-section-hd">
                <div className="mb-section-title">Live alerts</div>
                <div className="mb-section-pill">{alerts.length} items</div>
              </div>

              {loading ? (
                <div className="admin-empty-state">Loading alerts...</div>
              ) : visibleAlerts.length === 0 ? (
                <div className="admin-empty-state">No new alerts right now.</div>
              ) : (
                <div style={{ overflow: 'auto' }}>
                  <table className="mb-user-table" aria-label="Live alerts table">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Score</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Reason</th>
                        <th>Note</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visibleAlerts.map((alert) => (
                        <tr key={alert.id}>
                          <td>
                            <div className="mb-user-name-row">
                              <div className="mb-user-ava" style={{ background: 'linear-gradient(135deg,#7c6cff,#c084fc)' }}>
                                {(alert.user?.display_name || alert.user?.username || 'U').slice(0, 2).toUpperCase()}
                              </div>
                              <div>
                                <div style={{ fontSize: 12, fontWeight: 800 }}>{alert.user?.display_name || alert.user?.username}</div>
                                <div style={{ fontSize: 11, color: '#8882b0' }}>{alert.user?.email}</div>
                              </div>
                            </div>
                          </td>
                          <td style={{ fontWeight: 800, color: '#1a1635' }}>{Number(alert.score).toFixed(2)}</td>
                          <td>
                            <span className={`mb-risk-pill ${alert.severity >= 4 ? 'mb-risk-hi' : alert.severity === 3 ? 'mb-risk-med' : 'mb-risk-low'}`}>
                              S{alert.severity}
                            </span>
                          </td>
                          <td>
                            <span className="admin-status-pill">{alert.status.replace(/_/g, ' ')}</span>
                          </td>
                          <td style={{ color: '#1a1635', fontWeight: 600, whiteSpace: 'nowrap' }}>
                            {new Date(alert.created_at).toLocaleDateString()}
                          </td>
                          <td style={{ color: '#1a1635', fontWeight: 600, maxWidth: 320 }}>{alert.reason}</td>
                          <td>
                            <input
                              className="admin-note-input"
                              value={noteById[alert.id] || ''}
                              onChange={(e) => setNoteById((prev) => ({ ...prev, [alert.id]: e.target.value }))}
                              placeholder="Add note"
                            />
                          </td>
                          <td>
                            <div className="mb-action-row">
                              <button className="mini-button" onClick={() => handleAcknowledge(alert.id)}>Acknowledge</button>
                              <button className="mini-button secondary" onClick={() => handleResolve(alert.id)}>Resolve</button>
                              <button className="mini-button" onClick={() => openDetail(alert.id)}>View</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {/* Insights */}
            <section className="admin-panel admin-insights" style={{ marginTop: 0 }}>
              <div className="admin-panel-header" ref={sectionRefs.analytics}>
                <h2>Dashboard insights</h2>
              </div>
              <div className="insight-columns">
                <div className="insight-card">
                  <h3>What the model uses</h3>
                  <ul>
                    <li>Recent mood trend</li>
                    <li>Text risk keywords from journal notes</li>
                    <li>Tasks completed vs missed</li>
                    <li>Recent test activity</li>
                  </ul>
                </div>
                <div className="insight-card">
                  <h3>Review workflow</h3>
                  <ul>
                    <li>Acknowledge to mark “reviewed”</li>
                    <li>Resolve to close the case</li>
                    <li>Run scoring after retraining/feature updates</li>
                    <li>Inspect audits to verify reviewer actions</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Model manager (kept functional) */}
            <section ref={sectionRefs.model}>
              <ModelManager onRetrainComplete={() => loadData(statusFilter)} />
            </section>

            {/* Detail panel */}
            {selectedDetail && (
              <section className="admin-panel admin-detail-panel-wrap" style={{ marginTop: 16 }}>
                <AlertDetailPanel detail={selectedDetail} onClose={closeDetail} onActionComplete={handleDetailAction} />
              </section>
            )}

            {!selectedDetail && (
              <section className="admin-panel admin-detail-placeholder" style={{ marginTop: 16 }}>
                <div className="admin-panel-header">
                  <h2>Alert inspector</h2>
                  <span>Select any alert to see metadata, audit history, and reviewer actions.</span>
                </div>
                <div className="admin-placeholder-grid">
                  <div>
                    <div className="admin-placeholder-label">Current filter</div>
                    <div className="admin-placeholder-value">{currentStatusLabel}</div>
                  </div>
                  <div>
                    <div className="admin-placeholder-label">Visible alerts</div>
                    <div className="admin-placeholder-value">{alerts.length}</div>
                  </div>
                  <div>
                    <div className="admin-placeholder-label">Selected alert</div>
                    <div className="admin-placeholder-value">{selectedAlert ? `#${selectedAlert.id}` : 'None'}</div>
                  </div>
                  <div>
                    <div className="admin-placeholder-label">Last model run</div>
                    <div className="admin-placeholder-value">Use Model Manager</div>
                  </div>
                </div>
              </section>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

