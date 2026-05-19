import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showRegisterHint, setShowRegisterHint] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setErrors(err.data?.errors || ['Login failed. Please try again.']);
      if (err.data?.error_type === 'not_registered') setShowRegisterHint(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <h1>MindBloom</h1>
          <p>Your journey to self-discovery starts here</p>
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
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {showRegisterHint && (
          <div className="success-msg" style={{ background: '#EDE7F6', borderColor: '#D1C4E9', color: '#5E35B1', textAlign: 'center' }}>
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
