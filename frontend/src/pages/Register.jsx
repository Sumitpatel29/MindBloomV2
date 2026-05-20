import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';


export default function Register() {
  const { register, verifyOtpAndLogin } = useAuth();
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '', display_name: '' });
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [otpState, setOtpState] = useState({ step: 1, otp: '', otpSentEmail: '' });
  const [showPw, setShowPw] = useState(false);
  const [showConfirmPw, setShowConfirmPw] = useState(false);


  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);
    const errs = [];
    if (form.username.length < 3) errs.push('Username must be at least 3 characters.');
    if (!form.email.includes('@')) errs.push('Please enter a valid email.');
    if (form.password.length < 6) errs.push('Password must be at least 6 characters.');
    if (form.password !== form.confirmPassword) errs.push('Passwords do not match.');
    if (errs.length) { setErrors(errs); return; }

    setLoading(true);
    try {
      const res = await register(form.username, form.email, form.password, form.display_name);
      // OTP step
      if (res?.otp_required) {
        setOtpState({ step: 2, otp: '', otpSentEmail: res.email || form.email });
      } else {
        // fallback: some backend may still return token
        // do nothing; AuthContext will handle if token returned.
      }
    } catch (err) {
      setErrors(err.data?.errors || ['Registration failed. Please try again.']);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setErrors([]);
    setLoading(true);
    try {
      await verifyOtpAndLogin({ email: form.email, otp: otpState.otp, rememberMe: true });
      setOtpState((s) => ({ ...s, step: 1, otp: '', otpSentEmail: '' }));
    } catch (err) {
      setErrors(err.data?.errors || ['OTP verification failed.']);
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
              <p>Create your account to begin</p>
            </div>
            <div className="auth-chips">
              <span className="auth-chip">OTP verified</span>
              <span className="auth-chip">Secure onboarding</span>
            </div>
          </div>
        </div>


        {errors.length > 0 && (
          <div className="error-list">
            {errors.map((e, i) => <p key={i}>{e}</p>)}
          </div>
        )}

        {otpState.step === 1 ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">

              <label>Display Name</label>
              <input name="display_name" value={form.display_name} onChange={handleChange} placeholder="How should we call you?" />
            </div>
            <div className="form-group">
              <label>Username</label>
              <input name="username" value={form.username} onChange={handleChange} placeholder="Choose a username" required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="Enter your email" required />
            </div>

            <div className="form-group">
              <label>Password</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  name="password"
                  type={showPw ? 'text' : 'password'}
                  value={form.password}
                  onChange={handleChange}
                  placeholder="At least 6 characters"
                  required
                />
                <button type="button" className="btn btn-outline btn-sm" onClick={() => setShowPw((s) => !s)}>
                  {showPw ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  name="confirmPassword"
                  type={showConfirmPw ? 'text' : 'password'}
                  value={form.confirmPassword}
                  onChange={handleChange}
                  placeholder="Repeat your password"
                  required
                />
                <button type="button" className="btn btn-outline btn-sm" onClick={() => setShowConfirmPw((s) => !s)}>
                  {showConfirmPw ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp}>
            <div className="auth-alert auth-alert--hint">
              <p style={{ margin: 0 }}>
                OTP sent to <b>{otpState.otpSentEmail}</b>. Enter the 6-digit code to finish registration.
              </p>
            </div>


            <div className="form-group" style={{ marginTop: '16px' }}>
              <label>One-Time Password (OTP)</label>
              <input
                value={otpState.otp}
                onChange={(e) => setOtpState((s) => ({ ...s, otp: e.target.value }))}
                placeholder="6-digit code"
                inputMode="numeric"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? 'Verifying...' : 'Verify OTP'}
            </button>

            <div className="auth-link" style={{ marginTop: '14px' }}>
              Wrong email? <Link to="/register">Start over</Link>
            </div>

          </form>
        )}


        <div className="auth-link">
          Already have an account? <Link to="/login">Sign In</Link>
        </div>
      </div>
    </div>
  );
}
