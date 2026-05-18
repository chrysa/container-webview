import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import GlobalLoader from '@/components/loaders/GlobalLoader';
import styles from './Layout.module.scss';

export default function Layout() {
  return (
    <div className={styles.layout}>
      <Header />
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.content}>
          <Suspense fallback={<GlobalLoader />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
