import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import GlobalLoader from '@/components/loaders/GlobalLoader';
import Layout from '@/components/layouts/Layout';
import { isAuthenticated } from '@/utils/auth';

const Login = lazy(() => import('@/pages/Login'));
const Projects = lazy(() => import('@/pages/Projects'));
const Topology = lazy(() => import('@/pages/Topology'));
const Services = lazy(() => import('@/pages/Services'));
const Logs = lazy(() => import('@/pages/Logs'));
const Metrics = lazy(() => import('@/pages/Metrics'));
const Alerts = lazy(() => import('@/pages/Alerts'));
const NotFound = lazy(() => import('@/pages/NotFound'));

function RequireAuth({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<GlobalLoader />}>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="/projects" replace />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:projectId/topology" element={<Topology />} />
            <Route path="/projects/:projectId/services" element={<Services />} />
            <Route path="/projects/:projectId/logs" element={<Logs />} />
            <Route path="/projects/:projectId/metrics" element={<Metrics />} />
            <Route path="/alerts" element={<Alerts />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
