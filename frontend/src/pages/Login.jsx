import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [showPw, setShowPw] = useState(false);

  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showRegisterHint, setShowRegisterHint] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);
    setLoading(true);
    try {
      await login(email, password, rememberMe);
    } catch (err) {
      setErrors(err.data?.errors || ['Login failed. Please try again.']);
      if (err.data?.error_type === 'not_registered' || err.data?.error_type === 'email_not_verified') setShowRegisterHint(true);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-hero">
          <div className="auth-brand">
            <div className="auth-mark">MB</div>
            <div className="auth-logo">
              <h1>MindBloom</h1>
              <p>Your journey to self-discovery starts here</p>
            </div>
            <div className="auth-chips">
              <span className="auth-chip">Secure sign in</span>
              <span className="auth-chip">Private &amp; verified</span>
            </div>
          </div>
        </div>

        {errors.length > 0 && (
          <div className="error-list">
            {errors.map((e, i) => <p key={i}>{e}</p>)}
          </div>
        )}

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
              <button type="button" className="btn btn-outline btn-sm" onClick={() => setShowPw((s) => !s)}>
                {showPw ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} id="rememberMe" />
            <label htmlFor="rememberMe" style={{ margin: 0, cursor: 'pointer' }}>Remember me</label>
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {showRegisterHint && (
          <div className="auth-alert auth-alert--hint" style={{ textAlign: 'center' }}>
            <p style={{ marginBottom: '8px' }}>Looks like you don't have an account yet!</p>
            <Link to="/register" className="btn btn-primary btn-sm" style={{ display: 'inline-flex' }}>Create Account Now</Link>
          </div>
        )}


        <div className="auth-link">
          Don't have an account? <Link to="/register">Sign Up</Link>
        </div>
      </div>
    </div>
  );
}
