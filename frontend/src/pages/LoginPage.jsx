import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { MdOutlineReportProblem } from 'react-icons/md';
import { HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { login } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    const e = {};
    if (!email) e.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Invalid email format';
    if (!password) e.password = 'Password is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.name}!`);
      navigate(user.role === 'admin' ? '/admin' : '/complaints');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(msg);
      setErrors({ general: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4 animate-fade-in">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <MdOutlineReportProblem className="text-white text-2xl" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
          <p className="text-slate-500 mt-1">Sign in to your account</p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="login-email" className="label">Email Address</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={errors.email ? 'input-error' : 'input'}
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>

            <div>
              <label htmlFor="login-password" className="label">Password</label>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={errors.password ? 'input-error pr-10' : 'input pr-10'}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <HiOutlineEyeOff className="w-5 h-5" /> : <HiOutlineEye className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
            </div>

            {errors.general && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-red-600 text-sm">{errors.general}</p>
              </div>
            )}

            <button
              id="login-submit"
              type="submit"
              disabled={loading}
              className="btn-primary w-full btn-lg"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Quick Demo Login Buttons */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <p className="text-xs font-medium text-slate-400 text-center mb-3">QUICK DEMO ACCOUNTS</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                id="demo-citizen-btn"
                onClick={() => {
                  setEmail('test@gmail.com');
                  setPassword('test12');
                  setErrors({});
                }}
                className="px-3 py-2.5 bg-slate-50 hover:bg-primary-50 border border-slate-200 hover:border-primary-200 rounded-xl text-xs font-medium text-slate-700 flex flex-col items-center gap-0.5 transition-all group"
              >
                <span className="font-semibold text-primary-600 group-hover:text-primary-700">Citizen Account</span>
                <span className="text-[11px] text-slate-400">test@gmail.com</span>
              </button>
              <button
                type="button"
                id="demo-admin-btn"
                onClick={() => {
                  setEmail('admin@gmail.com');
                  setPassword('test12');
                  setErrors({});
                }}
                className="px-3 py-2.5 bg-slate-50 hover:bg-purple-50 border border-slate-200 hover:border-purple-200 rounded-xl text-xs font-medium text-slate-700 flex flex-col items-center gap-0.5 transition-all group"
              >
                <span className="font-semibold text-purple-600 group-hover:text-purple-700">Admin Account</span>
                <span className="text-[11px] text-slate-400">admin@gmail.com</span>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-sm text-slate-500 mt-6">
          Don't have an account?{' '}
          <Link to="/signup" className="text-primary-600 font-semibold hover:text-primary-700">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
