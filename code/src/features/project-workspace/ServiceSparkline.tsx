/**
 * ServiceSparkline — tiny inline metrics chart for the detail pane.
 * Uses recharts AreaChart; data comes from a rolling window of metric
 * snapshots accumulated in a ref (no backend change needed).
 *
 * Because useMetrics polls every 5 s, we accumulate up to 20 samples
 * (~100 s) in a module-level Map (keyed by project:service:metric) so the
 * trend survives remounts as the user navigates between services. The Map
 * is bounded (FIFO eviction past MAX_KEYS) so it cannot grow unbounded.
 */

import { useRef } from 'react';
import { AreaChart, Area, Tooltip, ResponsiveContainer } from 'recharts';
import type { ServiceMetrics } from '@/domain/metrics/types';
import styles from './ServiceSparkline.module.scss';

const STRINGS = {
  cpu: 'CPU %',
  mem: 'RAM MB',
  noData: 'Pas encore de données',
};

const MAX_SAMPLES = 20;
const MAX_KEYS = 256; // bound the store so it cannot grow unbounded across sessions

// keyed by `${projectId}:${serviceName}:${metric}`
const history = new Map<string, number[]>();

function pushSample(key: string, value: number): number[] {
  const arr = history.get(key) ?? [];
  const next = [...arr, value].slice(-MAX_SAMPLES);
  // FIFO eviction: Map preserves insertion order, so the first key is the oldest.
  if (!history.has(key) && history.size >= MAX_KEYS) {
    const oldest = history.keys().next().value;
    if (oldest !== undefined) history.delete(oldest);
  }
  history.set(key, next);
  return next;
}

interface Props {
  readonly projectId: string;
  readonly serviceName: string;
  readonly metrics: ServiceMetrics | undefined;
}

export default function ServiceSparkline({ projectId, serviceName, metrics }: Props) {
  const cpuKey = `${projectId}:${serviceName}:cpu`;
  const memKey = `${projectId}:${serviceName}:mem`;

  // push latest sample whenever metrics update
  const prevMetrics = useRef<ServiceMetrics | undefined>(undefined);
  if (metrics && metrics !== prevMetrics.current) {
    prevMetrics.current = metrics;
    pushSample(cpuKey, metrics.cpu_percent);
    pushSample(memKey, metrics.mem_usage_mb);
  }

  const cpuData = (history.get(cpuKey) ?? []).map((v, i) => ({ i, v }));
  const memData = (history.get(memKey) ?? []).map((v, i) => ({ i, v }));

  if (cpuData.length === 0 && memData.length === 0) {
    return <p className={styles.noData}>{STRINGS.noData}</p>;
  }

  return (
    <div className={styles.grid}>
      <div className={styles.chart}>
        <span className={styles.label}>{STRINGS.cpu}</span>
        <ResponsiveContainer width="100%" height={48}>
          <AreaChart data={cpuData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`cpu-${serviceName}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Tooltip
              formatter={(v) => [`${Number(v).toFixed(1)}%`, 'CPU']}
              contentStyle={{ fontSize: 11, padding: '2px 8px' }}
              wrapperStyle={{ zIndex: 10 }}
            />
            <Area
              type="monotone"
              dataKey="v"
              stroke="var(--primary)"
              fill={`url(#cpu-${serviceName})`}
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
        {metrics && <span className={styles.current}>{metrics.cpu_percent.toFixed(1)}%</span>}
      </div>

      <div className={styles.chart}>
        <span className={styles.label}>{STRINGS.mem}</span>
        <ResponsiveContainer width="100%" height={48}>
          <AreaChart data={memData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`mem-${serviceName}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--status-running)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--status-running)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Tooltip
              formatter={(v) => [`${Number(v).toFixed(0)} MB`, 'RAM']}
              contentStyle={{ fontSize: 11, padding: '2px 8px' }}
              wrapperStyle={{ zIndex: 10 }}
            />
            <Area
              type="monotone"
              dataKey="v"
              stroke="var(--status-running)"
              fill={`url(#mem-${serviceName})`}
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
        {metrics && (
          <span className={styles.current}>
            {metrics.mem_usage_mb.toFixed(0)} / {metrics.mem_limit_mb.toFixed(0)} MB
          </span>
        )}
      </div>
    </div>
  );
}
