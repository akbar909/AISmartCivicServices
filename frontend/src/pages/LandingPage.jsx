import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  HiOutlineLightningBolt, HiOutlineChartBar, HiOutlineChatAlt2, HiOutlineShieldCheck,
  HiOutlineArrowRight, HiOutlineSparkles, HiOutlineCheckCircle, HiOutlineGlobe
} from 'react-icons/hi';
import { MdOutlineReportProblem, MdOutlineSmartToy } from 'react-icons/md';
import landing3dHeroImg from '../assets/landing_3d_hero.png';

const features = [
  {
    icon: HiOutlineLightningBolt,
    title: 'AI Auto-Classification',
    description: 'Local scikit-learn models automatically categorize and prioritize complaints instantly upon typing.',
    color: 'from-amber-500 to-orange-500 text-amber-500 bg-amber-500/10 border-amber-500/20',
  },
  {
    icon: HiOutlineChatAlt2,
    title: 'Smart Guidance Chatbot',
    description: 'Get real-time help describing your issue. Our AI assistant suggests categories and answers questions.',
    color: 'from-teal-500 to-emerald-500 text-teal-500 bg-teal-500/10 border-teal-500/20',
  },
  {
    icon: HiOutlineChartBar,
    title: 'Real-Time Admin Analytics',
    description: 'Interactive analytics dashboards with department breakdown, priority distribution, and resolution tracking.',
    color: 'from-blue-500 to-indigo-500 text-blue-500 bg-blue-500/10 border-blue-500/20',
  },
  {
    icon: HiOutlineShieldCheck,
    title: 'End-to-End Transparency',
    description: 'Track your issue status live from submission to department assignment and final resolution.',
    color: 'from-purple-500 to-pink-500 text-purple-500 bg-purple-500/10 border-purple-500/20',
  },
];

const steps = [
  { num: '01', title: 'Describe Issue', desc: 'Detail the civic problem. AI predicts category & priority live as you type.' },
  { num: '02', title: 'Interactive Map Pin', desc: 'Get automatic GPS address or drag pin to lock exact coordinates.' },
  { num: '03', title: 'AI Photo Verification', desc: 'Local vision model verifies photo relevance and extracts visual evidence.' },
  { num: '04', title: 'Department Dispatch', desc: 'Auto-assigned to the appropriate department for fast resolution.' },
];

export default function LandingPage() {
  const { isAuthenticated, isAdmin } = useAuth();

  return (
    <div className="animate-fade-in space-y-16 overflow-hidden">
      {/* 3D Hero Section */}
      <section className="relative min-h-[85vh] bg-slate-950 text-white overflow-hidden flex items-center pt-8 pb-16">
        {/* Glowing Background Radial Accents */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-teal-500/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-emerald-500/15 rounded-full blur-[150px] pointer-events-none" />
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-30" />

        <div className="section relative z-10 w-full">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Hero Left Content */}
            <div className="lg:col-span-7 space-y-7">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs sm:text-sm font-semibold tracking-wide backdrop-blur-md shadow-lg shadow-teal-500/5">
                <HiOutlineSparkles className="w-4 h-4 text-teal-300 animate-pulse" />
                <span>Next-Gen AI Civic Infrastructure Platform</span>
              </div>

              <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-[1.1] text-white">
                Report Local Issues.{' '}
                <span className="bg-gradient-to-r from-teal-400 via-emerald-400 to-cyan-300 bg-clip-text text-transparent drop-shadow-sm">
                  Powered by AI.
                </span>
              </h1>

              <p className="text-base sm:text-xl text-slate-300 leading-relaxed font-normal max-w-2xl">
                AI Smart Civic Services combines scikit-learn machine learning, Gemini generative AI, and local PyTorch computer vision to classify, verify, and resolve city infrastructure grievances with unmatched speed.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
                {isAuthenticated ? (
                  <Link
                    to={isAdmin ? '/admin' : '/complaints/new'}
                    className="group px-7 py-4 rounded-2xl bg-gradient-to-r from-teal-500 via-emerald-500 to-teal-400 text-slate-950 font-extrabold text-base shadow-xl shadow-teal-500/25 hover:shadow-teal-500/40 hover:scale-[1.02] transition-all flex items-center justify-center gap-2"
                  >
                    <span>{isAdmin ? 'Go to Admin Dashboard' : 'Report a Civic Issue'}</span>
                    <HiOutlineArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                ) : (
                  <>
                    <Link
                      to="/signup"
                      className="group px-7 py-4 rounded-2xl bg-gradient-to-r from-teal-500 via-emerald-500 to-teal-400 text-slate-950 font-extrabold text-base shadow-xl shadow-teal-500/25 hover:shadow-teal-500/40 hover:scale-[1.02] transition-all flex items-center justify-center gap-2"
                    >
                      <span>Report a Civic Issue</span>
                      <HiOutlineArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                    <Link
                      to="/login"
                      className="px-7 py-4 rounded-2xl bg-slate-900/80 hover:bg-slate-800 text-white font-bold text-base border border-slate-700/80 hover:border-slate-500 backdrop-blur-md transition-all text-center"
                    >
                      Sign In
                    </Link>
                  </>
                )}
              </div>

              {/* Real Tech Stack Highlights Bar */}
              <div className="pt-6 border-t border-slate-800/80 grid grid-cols-3 gap-4">
                <div className="flex flex-col">
                  <span className="text-sm sm:text-base font-extrabold text-white flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-teal-400" /> Instant AI Routing
                  </span>
                  <span className="text-xs text-slate-400 font-medium">Auto-Categorize & Priority</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm sm:text-base font-extrabold text-teal-400 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" /> Live GPS & Map
                  </span>
                  <span className="text-xs text-slate-400 font-medium">Precision Pin & Address</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm sm:text-base font-extrabold text-white flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-cyan-400" /> AI Chatbot
                  </span>
                  <span className="text-xs text-slate-400 font-medium">Smart Filing Guidance</span>
                </div>
              </div>
            </div>

            {/* Hero Right 3D Showcase Card */}
            <div className="lg:col-span-5 perspective-1000">
              <div className="relative rotate-3d-card rounded-3xl bg-slate-900/90 border border-slate-700/60 p-4 shadow-2xl shadow-teal-500/20 backdrop-blur-2xl">
                {/* Image Showcase Container */}
                <div className="relative rounded-2xl overflow-hidden border border-slate-700/50 shadow-inner group">
                  <img
                    src={landing3dHeroImg}
                    alt="3D Smart City Dashboard"
                    className="w-full h-80 sm:h-96 object-cover object-center group-hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-80" />

                  {/* Floating 3D Badge 1 (Top Left) */}
                  <div className="absolute top-4 left-4 animate-float-slow bg-slate-900/90 backdrop-blur-md border border-teal-500/40 px-3.5 py-2 rounded-2xl shadow-xl flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                    <div>
                      <p className="text-[10px] uppercase font-bold text-teal-300 tracking-wider">AI Classification</p>
                      <p className="text-xs font-extrabold text-white">Road & Potholes (98%)</p>
                    </div>
                  </div>

                  {/* Floating 3D Badge 2 (Bottom Right) */}
                  <div className="absolute bottom-4 right-4 animate-float-reverse bg-slate-900/90 backdrop-blur-md border border-amber-500/40 px-3.5 py-2 rounded-2xl shadow-xl flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    <div>
                      <p className="text-[10px] uppercase font-bold text-amber-300 tracking-wider">Priority Rank</p>
                      <p className="text-xs font-extrabold text-amber-400">HIGH PRIORITY 🔥</p>
                    </div>
                  </div>
                </div>

                {/* Card Footer Info */}
                <div className="mt-3 px-2 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5 text-teal-400 font-medium">
                    <HiOutlineGlobe className="w-4 h-4" /> Live City Node Active
                  </span>
                  <span className="font-mono text-[11px] text-slate-500">HYD-NEO-2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Smarter Civic Services (3D Glass Cards) */}
      <section className="py-12 sm:py-20 relative">
        <div className="section">
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
            <h2 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight">
              Smarter Civic Infrastructure
            </h2>
            <p className="text-slate-500 text-base sm:text-lg">
              Integrating multi-model artificial intelligence to modernize city grievance handling.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f, i) => (
              <div
                key={i}
                className="group relative bg-white/90 backdrop-blur-xl rounded-3xl p-7 border border-slate-200/90 shadow-sm hover:shadow-2xl hover:shadow-teal-500/10 hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between"
              >
                <div>
                  <div className={`w-14 h-14 rounded-2xl border ${f.color} flex items-center justify-center mb-6 shadow-xs group-hover:scale-110 transition-transform duration-300`}>
                    <f.icon className="w-7 h-7" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-teal-700 transition-colors">
                    {f.title}
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed font-normal">
                    {f.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section (3D Step Pipeline) */}
      <section className="py-16 sm:py-24 bg-slate-900 text-white relative rounded-3xl my-8 overflow-hidden mx-4 sm:mx-8">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(13,148,136,0.15),transparent_70%)]" />
        <div className="section relative z-10">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <span className="px-3.5 py-1.5 rounded-full bg-teal-500/20 border border-teal-400/30 text-teal-300 text-xs font-bold uppercase tracking-wider">
              Seamless Workflow
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              4 Steps From Report To Resolution
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, i) => (
              <div
                key={i}
                className="relative bg-slate-800/80 backdrop-blur-md rounded-3xl p-6 border border-slate-700/80 hover:border-teal-500/50 hover:shadow-xl transition-all group"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-4xl font-black bg-gradient-to-br from-teal-400 to-emerald-300 bg-clip-text text-transparent group-hover:scale-110 transition-transform">
                    {step.num}
                  </span>
                  <div className="w-2.5 h-2.5 rounded-full bg-teal-400/60" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{step.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed font-normal">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3D Call To Action Section */}
      <section className="py-12 sm:py-16">
        <div className="section">
          <div className="relative overflow-hidden bg-gradient-to-r from-teal-900 via-slate-900 to-teal-950 rounded-3xl p-8 sm:p-14 text-center text-white shadow-2xl border border-teal-800/50">
            <div className="absolute -bottom-16 -right-16 w-80 h-80 bg-teal-500/20 rounded-full blur-3xl pointer-events-none" />
            <div className="relative z-10 max-w-2xl mx-auto space-y-6">
              <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
                Ready to improve your neighborhood?
              </h2>
              <p className="text-teal-200 text-sm sm:text-base font-normal leading-relaxed">
                File infrastructure complaints in seconds. Experience automatic ML categorization, live GPS pin location, and PyTorch photo verification.
              </p>
              <div className="pt-2">
                <Link
                  to={isAuthenticated ? '/complaints/new' : '/signup'}
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-white hover:bg-slate-100 text-slate-950 font-black text-base shadow-xl hover:shadow-2xl hover:scale-[1.03] transition-all"
                >
                  <span>Get Started Now</span>
                  <HiOutlineArrowRight className="w-5 h-5 text-teal-600" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
