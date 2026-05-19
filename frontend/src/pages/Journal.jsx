import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { journalAPI } from '../api/client';

const JOURNAL_TYPES = [
  { key: 'release_worry', title: 'Release Worry', desc: "Let go of the day's stressors.", icon: '🌿', bg: 'linear-gradient(135deg, #66BB6A, #43A047)' },
  { key: 'calm_anxiety', title: 'Calm Anxiety', desc: 'Understand your triggers.', icon: '💙', bg: 'linear-gradient(135deg, #42A5F5, #1E88E5)' },
  { key: 'feeling_angry', title: 'Feeling Angry', desc: 'Express and process anger.', icon: '🔥', bg: 'linear-gradient(135deg, #EF5350, #E53935)' },
  { key: 'feeling_happy', title: 'Feeling Happy', desc: 'Celebrate your joy!', icon: '☀️', bg: 'linear-gradient(135deg, #FFB74D, #FFA726)' },
];

const TYPE_ICONS = {
  release_worry: { icon: '🌿', bg: '#E8F5E9' },
  calm_anxiety: { icon: '💙', bg: '#E3F2FD' },
  feeling_angry: { icon: '🔥', bg: '#FFEBEE' },
  feeling_happy: { icon: '☀️', bg: '#FFF8E1' },
};

const MOOD_LABELS = ['', 'Very Sad', 'Sad', 'Normal', 'Happy', 'Very Happy'];

export default function Journal() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    journalAPI.getEntries().then(d => setEntries(d.entries)).catch(() => {});
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Journal</h1>
      </div>

      <div className="journal-types">
        {JOURNAL_TYPES.map(jt => (
          <Link key={jt.key} to={`/journal/${jt.key}`} className="journal-type-card" style={{ background: jt.bg }}>
            <span className="jt-icon">{jt.icon}</span>
            <span className="jt-title">{jt.title}</span>
            <span className="jt-desc">{jt.desc}</span>
          </Link>
        ))}
      </div>

      <div className="entries-section">
        <h2 className="section-title">📝 Your Entries</h2>
        {entries.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '30px' }}>
            <p style={{ fontSize: '40px', marginBottom: '8px' }}>📖</p>
            <h3 style={{ marginBottom: '4px' }}>No records yet</h3>
            <p style={{ color: 'var(--muted)', fontSize: '14px' }}>
              Engage in guided journaling activities daily and monitor your dynamics over time.
            </p>
          </div>
        ) : (
          entries.map(entry => {
            const style = TYPE_ICONS[entry.journal_type] || TYPE_ICONS.release_worry;
            return (
              <div key={entry.id} className="entry-item">
                <div className="entry-icon" style={{ background: style.bg }}>{style.icon}</div>
                <div className="entry-details">
                  <h4>{entry.journal_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</h4>
                  <p>Mood: {MOOD_LABELS[entry.mood] || 'Normal'} · {new Date(entry.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
