import { Navigate } from 'react-router-dom';
import LoginForm from '@/features/auth/LoginForm';
import { isAuthenticated } from '@/utils/auth';
import styles from './Login.module.scss';

export default function Login() {
  if (isAuthenticated()) return <Navigate to="/projects" replace />;
  return (
    <div className={styles.page}>
      <LoginForm />
    </div>
  );
}
