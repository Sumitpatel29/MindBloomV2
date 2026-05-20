import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('mindbloom_token');
    if (token) {
      authAPI.getMe()
        .then((data) => setUser(data.user))
        .catch((err) => {
          if (err && err.status === 401) {
            localStorage.removeItem('mindbloom_token');
          }
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }

    // Idle auto-logout (client-side)
    const idleMinutes = parseInt(import.meta.env.VITE_IDLE_LOGOUT_MINUTES || '30', 10);
    let lastActivity = Date.now();
    const logoutOnIdle = () => {
      const tokenNow = localStorage.getItem('mindbloom_token');
      if (!tokenNow) return;
      if (Date.now() - lastActivity >= idleMinutes * 60 * 1000) {
        localStorage.removeItem('mindbloom_token');
        setUser(null);
      }
    };

    const activityEvents = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
    const bump = () => { lastActivity = Date.now(); };
    activityEvents.forEach((ev) => window.addEventListener(ev, bump, { passive: true }));
    const timer = window.setInterval(logoutOnIdle, 60 * 1000);

    return () => {
      activityEvents.forEach((ev) => window.removeEventListener(ev, bump));
      window.clearInterval(timer);
    };
  }, []);


  const login = async (email, password, rememberMe = false) => {
    const data = await authAPI.login({ email, password, remember_me: rememberMe });
    localStorage.setItem('mindbloom_token', data.token);
    setUser(data.user);
    return data;
  };

  const register = async (username, email, password, display_name) => {
    // OTP flow: register does NOT return a token.
    const data = await authAPI.register({ username, email, password, display_name });
    return data;
  };

  const verifyOtpAndLogin = async ({ email, otp, rememberMe = false }) => {
    const data = await authAPI.verifyOtp({ email, otp, remember_me: rememberMe });
    localStorage.setItem('mindbloom_token', data.token);
    setUser(data.user);
    return data;
  };


  const logout = () => {
    localStorage.removeItem('mindbloom_token');
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const data = await authAPI.getMe();
      setUser(data.user);
    } catch (e) { /* ignore */ }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, verifyOtpAndLogin, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
