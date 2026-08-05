import './dashboard.css';
import { AuthenticatedNavbar } from '@/components/AuthenticatedNavbar';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-50">
        <AuthenticatedNavbar />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
      </div>
    </ProtectedRoute>
  );
}
