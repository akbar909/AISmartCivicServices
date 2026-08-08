import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import NewComplaintPage from './pages/NewComplaintPage';
import MyComplaintsPage from './pages/MyComplaintsPage';
import ComplaintDetailPage from './pages/ComplaintDetailPage';
import DashboardPage from './pages/DashboardPage';
import ComplaintsManagementPage from './pages/ComplaintsManagementPage';
import AdminComplaintDetailPage from './pages/AdminComplaintDetailPage';
import NotFoundPage from './pages/NotFoundPage';

export default function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            {/* Citizen Routes */}
            <Route
              path="/complaints/new"
              element={
                <ProtectedRoute requiredRole="citizen">
                  <NewComplaintPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/complaints"
              element={
                <ProtectedRoute requiredRole="citizen">
                  <MyComplaintsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/complaints/:id"
              element={
                <ProtectedRoute>
                  <ComplaintDetailPage />
                </ProtectedRoute>
              }
            />

            {/* Admin Routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRole="admin">
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/complaints"
              element={
                <ProtectedRoute requiredRole="admin">
                  <ComplaintsManagementPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/complaints/:id"
              element={
                <ProtectedRoute requiredRole="admin">
                  <AdminComplaintDetailPage />
                </ProtectedRoute>
              }
            />

            {/* 404 */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </ErrorBoundary>
  );
}
