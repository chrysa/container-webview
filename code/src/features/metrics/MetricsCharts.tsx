import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import { AlertCircle } from 'lucide-react';
import { useMetrics } from '@/domain/metrics/queries';
import styles from './MetricsCharts.module.scss';

const STATUS_CSS_VAR: Record<string, string> = {
  running: '--status-running',
  exited: '--status-exited',
  paused: '--status-paused',
  restarting: '--status-restarting',
  unknown: '--status-unknown',
};

function getStatusColor(status: string): string {
  const varName = STATUS_CSS_VAR[status] ?? '--status-unknown';
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim() || '#94a3b8';
}

interface Props {
  projectId: string;
}

export default function MetricsCharts({ projectId }: Readonly<Props>) {
  const { data, isLoading, error } = useMetrics(projectId);

  if (isLoading) return <div className={styles.state}>Chargement des métriques…</div>;
  if (error)
    return (
      <div className={styles.errorState}>
        <AlertCircle size={20} />
        <span>Erreur lors du chargement des métriques.</span>
      </div>
    );
  if (!data?.length) return <div className={styles.state}>Aucune donnée disponible.</div>;

  return (
    <div className={styles.grid}>
      {/* CPU */}
      <div className={styles.card}>
        <h3 className={styles.title}>CPU (%)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
            <XAxis dataKey="service" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, 'CPU']} />
            <Bar dataKey="cpu_percent" radius={[4, 4, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.service} fill={getStatusColor(entry.status)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Mémoire */}
      <div className={styles.card}>
        <h3 className={styles.title}>Mémoire (MB)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
            <XAxis dataKey="service" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => [`${v.toFixed(0)} MB`, 'RAM']} />
            <Legend />
            <Bar dataKey="mem_usage_mb" name="Utilisé" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="mem_limit_mb" name="Limite" fill="#64748b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Réseau */}
      <div className={styles.card}>
        <h3 className={styles.title}>Réseau (MB)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
            <XAxis dataKey="service" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="net_rx_mb" name="RX" fill="#22c55e" radius={[4, 4, 0, 0]} />
            <Bar dataKey="net_tx_mb" name="TX" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* I/O Disque */}
      <div className={styles.card}>
        <h3 className={styles.title}>I/O Disque (MB)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
            <XAxis dataKey="service" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="block_read_mb" name="Lecture" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="block_write_mb" name="Écriture" fill="#ec4899" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Tableau récap */}
      <div className={`${styles.card} ${styles.fullWidth}`}>
        <h3 className={styles.title}>Résumé</h3>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Service</th>
              <th>Statut</th>
              <th>CPU%</th>
              <th>RAM (MB)</th>
              <th>RAM%</th>
            </tr>
          </thead>
          <tbody>
            {data.map((m) => (
              <tr key={m.service}>
                <td>{m.service}</td>
                <td>
                  <span className={[styles.status, styles[`status_${m.status}`]].join(' ')}>{m.status}</span>
                </td>
                <td>{m.cpu_percent.toFixed(2)}%</td>
                <td>
                  {m.mem_usage_mb.toFixed(0)} / {m.mem_limit_mb.toFixed(0)}
                </td>
                <td>{m.mem_percent.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
