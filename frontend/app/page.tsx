import Link from 'next/link';
import { AuthenticatedNavbar } from '@/components/AuthenticatedNavbar';
import { ArrowRight, BarChart3, BrainCircuit, CheckCircle2, ChevronRight, ShieldCheck, Sparkles } from 'lucide-react';

const features = [
  {
    icon: BrainCircuit,
    title: 'AI Evaluation',
    description: 'Get IELTS-style writing and speaking feedback with actionable suggestions and score estimates.',
  },
  {
    icon: BarChart3,
    title: 'Detailed Analytics',
    description: 'Track your progress across sections and skill areas with clean, exam-focused insights.',
  },
  {
    icon: ShieldCheck,
    title: 'Real Exam Simulation',
    description: 'Practice within a timed environment that mirrors the pressure and structure of the real IELTS test.',
  },
];

const steps = [
  'Create your account and choose a mock test.',
  'Complete the timed exam under realistic conditions.',
  'Review AI feedback and improve your weak areas.',
];

const faqs = [
  {
    question: 'Is BandUp IELTS suitable for IELTS preparation?',
    answer: 'Yes. BandUp IELTS is built around IELTS-style practice, section simulations, and feedback for writing and speaking.',
  },
  {
    question: 'Can I practice without paying?',
    answer: 'The landing experience is designed to let you explore the platform and begin free mock test practice.',
  },
  {
    question: 'Does the platform include analytics?',
    answer: 'Yes. The dashboard tracks recent performance trends, weak areas, and section-level progress for continuous improvement.',
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <AuthenticatedNavbar />
      <section className="relative overflow-hidden border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-20 lg:px-8">
            <div className="hidden">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500 font-bold text-slate-950">B</div>
                <span className="text-lg font-semibold tracking-tight text-slate-900">BandUp IELTS</span>
            </div>
            <div className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
              <Link href="#features" className="hover:text-white">Features</Link>
              <Link href="#how-it-works" className="hover:text-white">How it works</Link>
              <Link href="#faq" className="hover:text-white">FAQ</Link>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/login" className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:border-sky-400 hover:text-white">Login</Link>
              <Link href="/register" className="rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400">Get started</Link>
            </div>
            </div>

          <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-sky-200">
                <Sparkles className="h-3.5 w-3.5" />
                IELTS prep, upgraded
              </div>
              <h1 className="mt-6 max-w-xl text-5xl font-black tracking-tight text-slate-900 lg:text-6xl">
                Practice smarter. Score higher.
              </h1>
              <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
                Master IELTS with realistic mock tests, writing and speaking evaluation, and a clear plan to improve every band score.
              </p>
              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Link href="/tests" aria-label="Start free mock test" className="inline-flex items-center justify-center gap-2 rounded-full bg-sky-500 px-6 py-3 text-base font-semibold text-slate-950 transition hover:bg-sky-400">
                  Start Free Mock Test
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link href="/login" aria-label="Log in to BandUp IELTS" className="inline-flex items-center justify-center rounded-full border border-slate-300 bg-white px-6 py-3 text-base font-semibold text-slate-900 transition hover:border-sky-500 hover:bg-slate-50">
                  Login
                </Link>
              </div>
              <div className="mt-10 flex flex-wrap items-center gap-5 text-sm text-slate-300">
                <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> 4 full IELTS sections</span>
                <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> Real-time progress tracking</span>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-sky-950/30 backdrop-blur">
              <p className="text-xs font-medium uppercase tracking-[0.25em] text-sky-300">Your practice path</p>
              <h2 className="mt-5 text-2xl font-bold text-white">Take a test, get feedback, keep improving.</h2>
              <p className="mt-4 text-sm leading-7 text-slate-300">Your personal dashboard fills with real scores and recommendations after your first completed mock test.</p>
              <Link href="/tests" className="mt-6 inline-flex items-center gap-2 font-semibold text-sky-300 hover:text-sky-200">Explore mock tests <ArrowRight className="h-4 w-4" /></Link>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-6 py-20 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-400">Features</p>
          <h2 className="mt-4 text-3xl font-bold text-slate-900 dark:text-white md:text-4xl">Everything you need to improve faster.</h2>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {features.map(({ icon: Icon, title, description }) => (
            <div key={title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-900/5 dark:border-slate-800 dark:bg-slate-900">
              <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-500/10 text-sky-600 dark:text-sky-300">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white">{title}</h3>
              <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="bg-slate-100 py-20 dark:bg-slate-900/70">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-500">How it works</p>
            <h2 className="mt-4 text-3xl font-bold text-slate-900 dark:text-white md:text-4xl">Your path to a stronger band score.</h2>
          </div>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-full bg-sky-500 font-semibold text-slate-950">{index + 1}</div>
                <p className="text-base leading-7 text-slate-700 dark:text-slate-200">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="faq" className="mx-auto max-w-5xl px-6 py-20 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-500">FAQ</p>
          <h2 className="mt-4 text-3xl font-bold text-slate-900 dark:text-white md:text-4xl">Common questions, answered.</h2>
        </div>
        <div className="mt-12 space-y-4">
          {faqs.map(({ question, answer }) => (
            <div key={question} className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
              <div className="flex items-center justify-between gap-4 text-left">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{question}</h3>
                <ChevronRight className="h-4 w-4 text-slate-500" />
              </div>
              <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">{answer}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8 text-sm text-slate-600 dark:text-slate-300 md:flex-row md:items-center md:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500 font-bold text-slate-950">B</div>
            <span className="font-semibold text-slate-900">BandUp IELTS</span>
          </div>
          <div className="flex flex-wrap items-center gap-5">
            <Link href="/tests" className="hover:text-slate-900 dark:hover:text-white">Tests</Link>
            <Link href="/dashboard" className="hover:text-slate-900 dark:hover:text-white">Dashboard</Link>
            <Link href="/analytics" className="hover:text-slate-900 dark:hover:text-white">Analytics</Link>
            <Link href="/login" className="hover:text-slate-900 dark:hover:text-white">Login</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
