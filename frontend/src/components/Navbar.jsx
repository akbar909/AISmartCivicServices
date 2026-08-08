import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineMenu, HiOutlineX, HiOutlineUserCircle } from 'react-icons/hi';
import { MdOutlineReportProblem } from 'react-icons/md';
import NotificationBell from './NotificationBell';

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    setProfileOpen(false);
  };

  const citizenLinks = [
    { to: '/complaints/new', label: 'Report Issue' },
    { to: '/complaints', label: 'My Complaints' },
  ];

  const adminLinks = [
    { to: '/admin', label: 'Dashboard' },
    { to: '/admin/complaints', label: 'Manage Complaints' },
  ];

  const links = isAdmin ? adminLinks : citizenLinks;

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
      <div className="section">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 bg-gradient-primary rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow">
              <MdOutlineReportProblem className="text-white text-lg" />
            </div>
            <span className="text-lg font-bold text-slate-900 hidden sm:block">
              Smart<span className="text-primary-600">Civic</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {isAuthenticated && links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:text-primary-600 hover:bg-primary-50 transition-all"
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2">
            {/* Notification Bell */}
            <NotificationBell />
            {isAuthenticated ? (
              <div className="relative">
                <button
                  id="profile-menu-trigger"
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-slate-100 transition-all"
                >
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-700 font-semibold text-sm">
                      {user?.name?.charAt(0)?.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-slate-700 hidden sm:block">
                    {user?.name}
                  </span>
                </button>

                {/* Dropdown */}
                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-lg border border-slate-200 py-2 animate-slide-down">
                    <div className="px-4 py-2 border-b border-slate-100">
                      <p className="text-sm font-medium text-slate-900">{user?.name}</p>
                      <p className="text-xs text-slate-500">{user?.email}</p>
                      <span className="inline-block mt-1 px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full text-xs font-medium capitalize">
                        {user?.role}
                      </span>
                    </div>
                    <button
                      id="logout-button"
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login" className="btn-ghost btn-sm">
                  Log In
                </Link>
                <Link to="/signup" className="btn-primary btn-sm">
                  Sign Up
                </Link>
              </div>
            )}

            {/* Mobile menu button */}
            <button
              id="mobile-menu-toggle"
              className="md:hidden p-2 rounded-xl hover:bg-slate-100"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <HiOutlineX className="w-5 h-5" /> : <HiOutlineMenu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <div className="md:hidden py-4 border-t border-slate-100 animate-slide-down">
            {isAuthenticated && links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileOpen(false)}
                className="block px-4 py-3 rounded-xl text-sm font-medium text-slate-600 hover:bg-primary-50 hover:text-primary-600"
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
