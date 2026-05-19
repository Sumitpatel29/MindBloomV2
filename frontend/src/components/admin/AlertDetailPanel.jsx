import React, { useState } from 'react';
import { adminAPI } from '../../api/client';
import AuditTimeline from './AuditTimeline';

export default function AlertDetailPanel({ detail, onClose, onActionComplete }) {
  const [loading, setLoading] = useState(false);
  if (!detail) return null;
  const { alert, user, audits } = detail;
  const metadata = alert.metadata || {};
  const reviewer = alert.reviewed_by_user || null;

  const statusLabel = alert.status.replace(/_/g, ' ');
  const createdAt = new Date(alert.created_at).toLocaleString();
  const reviewedAt = alert.reviewed_at ? new Date(alert.reviewed_at).toLocaleString() : 'Not reviewed yet';

  const doAck = async () => {
    setLoading(true);
    try {
      await adminAPI.acknowledge(alert.id, 'Acknowledged via detail panel');
      if (onActionComplete) onActionComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const doResolve = async () => {
    setLoading(true);
    try {
      await adminAPI.resolve(alert.id, 'Resolved via detail panel', 'resolved');
      if (onActionComplete) onActionComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="alert-detail-panel">
      <div className="alert-detail-header">
        <div>
          <div className="admin-detail-kicker">Selected alert</div>
          <h3>Alert #{alert.id} • Severity {alert.severity}</h3>
        </div>
        <div className="admin-status-pill-wrap">
          <span className={`admin-status-pill severity-${alert.severity}`}>{statusLabel}</span>
          <button className="mini-button" onClick={onClose}>Close</button>
        </div>
      </div>
      <div className="admin-detail-summary">
        <div className="admin-detail-summary-item">
          <span>Score</span>
          <strong>{Number(alert.score).toFixed(3)}</strong>
        </div>
        <div className="admin-detail-summary-item">
          <span>Severity</span>
          <strong>S{alert.severity}</strong>
        </div>
        <div className="admin-detail-summary-item">
          <span>Created</span>
          <strong>{createdAt}</strong>
        </div>
        <div className="admin-detail-summary-item">
          <span>Reviewed</span>
          <strong>{reviewedAt}</strong>
        </div>
      </div>
      <div className="alert-detail-body">
        <div className="alert-section">
          <h4>User</h4>
          <div className="alert-user-line">
            <span className="alert-user-name">{user?.display_name || user?.username}</span>
            <span className="muted">{user?.email}</span>
          </div>
        </div>
        <div className="alert-section">
          <h4>Score & Reason</h4>
          <div className="alert-reason">{alert.reason}</div>
          <div className="admin-metadata-grid">
            <div>
              <span>Row index</span>
              <strong>{metadata.row_index ?? '—'}</strong>
            </div>
            <div>
              <span>Model score</span>
              <strong>{Number(metadata.iso_score ?? alert.score).toFixed(3)}</strong>
            </div>
            <div>
              <span>Risk signal</span>
              <strong>{Number(metadata.reconstruction_error ?? 0).toFixed(3)}</strong>
            </div>
            <div>
              <span>Reviewer</span>
              <strong>{reviewer?.display_name || reviewer?.username || 'Not assigned'}</strong>
            </div>
          </div>
        </div>
        <div className="alert-section">
          <h4>Audits</h4>
          <AuditTimeline audits={audits} />
        </div>
      </div>
      <div className="alert-detail-actions">
        <button className="admin-button primary" onClick={doAck} disabled={loading}>Acknowledge</button>
        <button className="admin-button" onClick={doResolve} disabled={loading}>Resolve</button>
      </div>
    </div>
  );
}
