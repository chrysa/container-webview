export interface ServiceMetrics {
  service: string;
  container_id: string;
  status: string;
  cpu_percent: number;
  mem_usage_mb: number;
  mem_limit_mb: number;
  mem_percent: number;
  net_rx_mb: number;
  net_tx_mb: number;
  block_read_mb: number;
  block_write_mb: number;
}
