export interface Alert {
  id: string;
  level: 'info' | 'warning' | 'critical';
  project: string;
  service: string;
  message: string;
  timestamp: string;
}
