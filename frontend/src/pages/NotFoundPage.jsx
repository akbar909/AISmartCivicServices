import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center animate-fade-in">
      <div className="text-center">
        <h1 className="text-8xl font-extrabold text-primary-100">404</h1>
        <h2 className="text-2xl font-bold text-slate-900 mt-4 mb-2">Page Not Found</h2>
        <p className="text-slate-500 mb-8 max-w-md">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to="/" className="btn-primary btn-lg">
          Back to Home
        </Link>
      </div>
    </div>
  );
}
