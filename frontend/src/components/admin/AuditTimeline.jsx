import React from 'react';

export default function AuditTimeline({ audits = [] }) {
  if (!audits || audits.length === 0) return <div className="audit-empty">No audits yet.</div>;
  return (
    <div className="audit-timeline">
      {audits.map((a) => (
        <div key={a.id} className="audit-item">
          <div className="audit-meta">
            <strong>{a.action}</strong> &middot; <span className="muted">{new Date(a.created_at).toLocaleString()}</span>
          </div>
          {a.note && <div className="audit-note">{a.note}</div>}
          {a.actor && <div className="audit-actor muted">By: {a.actor.display_name || a.actor.username}</div>}
          {!a.actor && a.actor_id && <div className="audit-actor muted">By actor #{a.actor_id}</div>}
        </div>
      ))}
    </div>
  );
}
