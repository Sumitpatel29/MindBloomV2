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
          // Only remove the token if it is actually invalid/expired (401).
          // Do NOT remove it on network errors (backend not started yet, etc.)
          // so that the user stays logged in when they restart the backend.
          if (err && err.status === 401) {
            localStorage.removeItem('mindbloom_token');
          }
          // For any other error (network down, 500, etc.) keep the token —
          // the user will be shown the login page but won't lose their account.
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const data = await authAPI.login({ email, password });
    localStorage.setItem('mindbloom_token', data.token);
    setUser(data.user);
    return data;
  };

  const register = async (username, email, password, display_name) => {
    const data = await authAPI.register({ username, email, password, display_name });
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
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
