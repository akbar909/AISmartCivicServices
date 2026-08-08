import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { login as loginApi, signup as signupApi, getMe } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, check for stored token and fetch user
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await getMe();
          setUser(userData);
        } catch {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await loginApi({ email, password });
    localStorage.setItem('token', data.access_token);
    const userData = await getMe();
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    return userData;
  }, []);

  const signup = useCallback(async (name, email, password, role = 'citizen') => {
    await signupApi({ name, email, password, role });
    // Auto-login after signup
    return await login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isCitizen: user?.role === 'citizen',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
