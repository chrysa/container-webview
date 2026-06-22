import { Suspense, lazy } from 'react';
import { createBrowserRouter, RouterProvider, Navigate, type RouteObject } from 'react-router-dom';
import GlobalLoader from '@/components/loaders/GlobalLoader';
import Layout from '@/components/layouts/Layout';
import { ToastProvider } from '@/components/feedback/Toast';
import { DemoBanner } from '@/components/ui/DemoBanner';
import { isAuthenticated } from '@/utils/auth';

const Login = lazy(() => import('@/pages/Login'));
const Projects = lazy(() => import('@/pages/Projects'));
const ProjectWorkspacePage = lazy(() => import('@/pages/ProjectWorkspacePage'));
const Topology = lazy(() => import('@/pages/Topology'));
const Services = lazy(() => import('@/pages/Services'));
const Logs = lazy(() => import('@/pages/Logs'));
const Metrics = lazy(() => import('@/pages/Metrics'));
const Alerts = lazy(() => import('@/pages/Alerts'));
const NotFound = lazy(() => import('@/pages/NotFound'));

function RequireAuth({ children }: Readonly<{ children: React.ReactNode }>) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

// A data router is required because the layout consumes `useMatches()`
// (breadcrumbs). `createBrowserRouter` provides the matches context that the
// legacy `<BrowserRouter>` did not.
const routes: RouteObject[] = [
  { path: '/login', element: <Login /> },
  {
    element: (
      <RequireAuth>
        <Layout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/projects" replace /> },
      { path: '/projects', element: <Projects /> },
      { path: '/projects/:projectId', element: <ProjectWorkspacePage /> },
      { path: '/projects/:projectId/topology', element: <Topology /> },
      { path: '/projects/:projectId/services', element: <Services /> },
      { path: '/projects/:projectId/logs', element: <Logs /> },
      { path: '/projects/:projectId/metrics', element: <Metrics /> },
      { path: '/alerts', element: <Alerts /> },
    ],
  },
  { path: '*', element: <NotFound /> },
];

const router = createBrowserRouter(routes);

export default function App() {
  return (
    <ToastProvider>
      <DemoBanner />
      <Suspense fallback={<GlobalLoader />}>
        <RouterProvider router={router} />
      </Suspense>
    </ToastProvider>
  );
}
