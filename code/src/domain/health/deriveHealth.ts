/**
 * Client-side health derivation.
 *
 * The backend exposes ServiceMetrics.status (the raw Docker status string)
 * and Alert records that correlate project + service + exit/unhealthy events.
 * There is no first-class per-service "status" field on the Project/Service
 * type — we derive it here from the two queries we already fetch.
 *
 * FOLLOW-UP: backend should expose a first-class service.status field so the
 * projects query alone is enough and we avoid the metrics-query dependency for
 * the health badge.
 */

import type { ServiceMetrics } from '@/domain/metrics/types';
import type { Alert } from '@/domain/alerts/types';

export type HealthStatus = 'running' | 'exited' | 'restarting' | 'paused' | 'unhealthy' | 'unknown';

/**
 * Map a raw (lower-cased) Docker status string to a HealthStatus, or undefined
 * for any unexpected string (which is treated as "unknown" by the caller).
 */
function mapDockerStatus(status: string): HealthStatus | undefined {
  const s = status.toLowerCase();
  if (s === 'running') return 'running';
  if (s === 'exited') return 'exited';
  if (s === 'restarting') return 'restarting';
  if (s === 'paused') return 'paused';
  if (s.includes('unhealthy')) return 'unhealthy';
  return undefined;
}

/**
 * Derive a single health status for a service name given the current snapshot
 * from the metrics query and the alerts query.
 *
 * Priority order (most severe wins):
 *   1. metrics.status if available   → direct Docker status string
 *   2. alert-derived unhealthy/exited → alerts_service already correlates
 *      unhealthy/exit_code events; if no metrics entry but a critical alert
 *      exists for the service we surface "unhealthy"
 *   3. unknown                        → neither source has data yet
 */
export function deriveServiceHealth(
  serviceName: string,
  metrics: ServiceMetrics[] | undefined,
  alerts: Alert[] | undefined
): HealthStatus {
  // 1. metrics path (most accurate — live Docker status)
  const m = metrics?.find((e) => e.service === serviceName);
  if (m) {
    const mapped = mapDockerStatus(m.status);
    if (mapped) return mapped;
    // pass through as unknown for any unexpected string
  }

  // 2. alert-derived path
  if (alerts) {
    const serviceAlerts = alerts.filter((a) => a.service === serviceName);
    const hasCritical = serviceAlerts.some((a) => a.level === 'critical');
    if (hasCritical) return 'unhealthy';
    const hasWarning = serviceAlerts.some((a) => a.level === 'warning');
    if (hasWarning) return 'exited'; // exit_code alerts are warning-level by convention
  }

  return 'unknown';
}

/**
 * Aggregate health for an entire project: worst status wins.
 */
const SEVERITY: Record<HealthStatus, number> = {
  unhealthy: 5,
  exited: 4,
  restarting: 3,
  paused: 2,
  unknown: 1,
  running: 0,
};

export function deriveProjectHealth(
  serviceNames: string[],
  metrics: ServiceMetrics[] | undefined,
  alerts: Alert[] | undefined
): HealthStatus {
  if (serviceNames.length === 0) return 'unknown';
  return serviceNames.reduce<HealthStatus>((worst, svc) => {
    const h = deriveServiceHealth(svc, metrics, alerts);
    return SEVERITY[h] > SEVERITY[worst] ? h : worst;
  }, 'running');
}
