import { MdOutlineReportProblem } from 'react-icons/md';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto">
      <div className="section py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-primary rounded-lg flex items-center justify-center">
              <MdOutlineReportProblem className="text-white text-sm" />
            </div>
            <span className="text-sm font-semibold text-slate-700">
              Smart<span className="text-primary-600">Civic</span>
            </span>
          </div>
          <p className="text-xs text-slate-400">
            © {new Date().getFullYear()} AI Smart Civic Services. Powered by AI for better cities.
          </p>
        </div>
      </div>
    </footer>
  );
}
