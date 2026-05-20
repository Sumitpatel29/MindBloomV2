import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { profileAPI } from '../api/client';

export default function Profile() {
  const { user, logout, refreshUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [changingPw, setChangingPw] = useState(false);
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' });
  const [msg, setMsg] = useState('');
  const [errors, setErrors] = useState([]);

  const handleSaveProfile = async () => {
    try {
      await profileAPI.update({ display_name: displayName });
      await refreshUser();
      setEditing(false);
      setMsg('Profile updated!');
      setTimeout(() => setMsg(''), 3000);
    } catch (e) {
      setErrors(['Failed to update profile.']);
    }
  };

  const handleChangePw = async () => {
    setErrors([]);
    if (pwForm.newPw.length < 6) { setErrors(['New password must be at least 6 characters.']); return; }
    if (pwForm.newPw !== pwForm.confirm) { setErrors(['Passwords do not match.']); return; }
    try {
      await profileAPI.changePassword(pwForm.current, pwForm.newPw);
      setChangingPw(false);
      setPwForm({ current: '', newPw: '', confirm: '' });
      setMsg('Password changed!');
      setTimeout(() => setMsg(''), 3000);
    } catch (e) {
      setErrors(e.data?.errors || ['Failed to change password.']);
    }
  };

  if (!user) return null;
  const initial = (user.display_name || user.username || '?')[0].toUpperCase();

  return (
    <div className="page profile-page">
      <div className="profile-header">
        <div className="avatar">{initial}</div>
        <h2>{user.display_name || user.username}</h2>
        <p>@{user.username} · {user.email}</p>
      </div>

      {msg && <div className="success-msg">{msg}</div>}
      {errors.length > 0 && <div className="error-list">{errors.map((e, i) => <p key={i}>{e}</p>)}</div>}

      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-num">{user.stats?.journal_entries || 0}</div>
          <div className="stat-label">Journal Entries</div>
        </div>
        <div className="stat-item">
          <div className="stat-num">{user.stats?.tests_taken || 0}</div>
          <div className="stat-label">Tests Taken</div>
        </div>
        <div className="stat-item">
          <div className="stat-num">{user.stats?.assessments_done || 0}</div>
          <div className="stat-label">Assessments</div>
        </div>
      </div>

      <div className="profile-menu">
        {!editing ? (
          <button className="menu-item" onClick={() => setEditing(true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            <span>Edit Profile</span>
          </button>
        ) : (
          <div className="card" style={{ padding: '16px' }}>
            <div className="form-group">
              <label>Display Name</label>
              <input value={displayName} onChange={e => setDisplayName(e.target.value)} />
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-primary btn-sm" onClick={handleSaveProfile}>Save</button>
              <button className="btn btn-outline btn-sm" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </div>
        )}

        {!changingPw ? (
          <button className="menu-item" onClick={() => setChangingPw(true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            <span>Change Password</span>
          </button>
        ) : (
          <div className="card" style={{ padding: '16px' }}>
            <div className="form-group">
              <label>Current Password</label>
              <input type="password" value={pwForm.current} onChange={e => setPwForm({ ...pwForm, current: e.target.value })} />
            </div>
            <div className="form-group">
              <label>New Password</label>
              <input type="password" value={pwForm.newPw} onChange={e => setPwForm({ ...pwForm, newPw: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Confirm New Password</label>
              <input type="password" value={pwForm.confirm} onChange={e => setPwForm({ ...pwForm, confirm: e.target.value })} />
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-primary btn-sm" onClick={handleChangePw}>Save</button>
              <button className="btn btn-outline btn-sm" onClick={() => setChangingPw(false)}>Cancel</button>
            </div>
          </div>
        )}

        <button className="menu-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          <span>Settings</span>
        </button>

        <button className="menu-item danger" onClick={logout}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          <span>Log Out</span>
        </button>
      </div>

      <p style={{ textAlign: 'center', color: 'var(--muted)', fontSize: '12px', marginTop: '24px' }}>
        Member since {new Date(user.created_at).toLocaleDateString()}
      </p>
    </div>
  );
}
