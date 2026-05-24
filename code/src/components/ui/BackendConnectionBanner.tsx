import { useBackendStatus } from "../../hooks/useBackendStatus";
import styles from "./BackendConnectionBanner.module.scss";

const DISCONNECTED_MSG =
  "Unable to reach the server. Please check your connection.";

export function BackendConnectionBanner() {
  const isBackendDown = useBackendStatus();

  if (!isBackendDown) return null;

  return (
    <div
      className={styles.banner}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <span className={styles.icon} aria-hidden="true">
        ⚠️
      </span>
      <span className={styles.message}>{DISCONNECTED_MSG}</span>
    </div>
  );
}
