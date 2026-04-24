import { useEffect, useRef, useState } from 'react';
import { useProject } from '@/domain/projects/queries';
import { getToken } from '@/utils/auth';
import styles from './LogsPanel.module.scss';

interface Props {
  projectId: string;
}

function LogViewer({ projectId, serviceName }: Readonly<{ projectId: string; serviceName: string }>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [lines, setLines] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    setLines([]);
    const token = getToken() ?? '';
    const protocol = globalThis.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${globalThis.location.host}/api/projects/${projectId}/services/${serviceName}/logs?token=${encodeURIComponent(token)}&tail=200`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (ev) => {
      setLines((prev) => {
        const next = [...prev, ev.data as string];
        return next.length > 2000 ? next.slice(-2000) : next;
      });
    };

    return () => {
      ws.close();
    };
  }, [projectId, serviceName]);

  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll conditionnel
  useEffect(() => {
    const el = containerRef.current;
    if (el && autoScroll) el.scrollTop = el.scrollHeight;
  }, [lines, autoScroll]);

  function handleScroll() {
    const el = containerRef.current;
    if (!el) return;
    const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 20;
    setAutoScroll(atBottom);
  }

  return (
    <div className={styles.viewer}>
      <div className={styles.viewerHeader}>
        <span className={`${styles.dot} ${connected ? styles.dotOnline : styles.dotOffline}`} />
        <span>{serviceName}</span>
        <span className={styles.countBadge}>{lines.length} lignes</span>
        <button
          className={`${styles.scrollBtn} ${autoScroll ? styles.scrollBtnActive : ''}`}
          onClick={() => {
            setAutoScroll((v) => {
              if (!v && containerRef.current) containerRef.current.scrollTop = containerRef.current.scrollHeight;
              return !v;
            });
          }}
          title={autoScroll ? 'Auto-scroll actif' : 'Auto-scroll désactivé'}
        >
          Auto-scroll
        </button>
        <button className={styles.clearBtn} onClick={() => setLines([])}>
          Vider
        </button>
      </div>
      <div ref={containerRef} className={styles.terminal} onScroll={handleScroll}>
        {lines.map((line, i) => (
          // eslint-disable-next-line react/no-array-index-key -- log lines have no unique ID
          <div key={i} className={styles.line}>
            {line}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function LogsPanel({ projectId }: Readonly<Props>) {
  const { data: project, isLoading } = useProject(projectId);
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (project?.services[0] && !active) {
      setActive(project.services[0].name);
    }
  }, [project, active]);

  if (isLoading) return <div className={styles.state}>Chargement…</div>;
  if (!project) return <div className={styles.state}>Projet introuvable.</div>;

  return (
    <div className={styles.wrapper}>
      <div className={styles.tabs}>
        {project.services.map((svc) => (
          <button
            key={svc.name}
            className={`${styles.tab} ${active === svc.name ? styles.tabActive : ''}`}
            onClick={() => setActive(svc.name)}
          >
            {svc.name}
          </button>
        ))}
      </div>
      {active && <LogViewer projectId={projectId} serviceName={active} />}
    </div>
  );
}
