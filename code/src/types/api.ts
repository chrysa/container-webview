export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  username: string
}

export interface ServiceModel {
  name: string
  image: string | null
  ports: string[]
  volumes: string[]
  environment: Record<string, string>
  networks: string[]
  depends_on: string[]
}

export interface ProjectModel {
  id: string
  name: string
  path: string
  compose_file: string
  services: ServiceModel[]
  networks: string[]
}

export interface ServiceMetrics {
  service: string
  container_id: string
  status: string
  cpu_percent: number
  mem_usage_mb: number
  mem_limit_mb: number
  mem_percent: number
  net_rx_mb: number
  net_tx_mb: number
  block_read_mb: number
  block_write_mb: number
}

export interface Alert {
  id: string
  project: string
  service: string
  level: 'info' | 'warning' | 'critical'
  message: string
  timestamp: string
}

export interface GraphNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: Record<string, unknown>
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  label?: string
}

export interface TopologyGraph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface ActionResponse {
  service: string
  action: string
  status: string
  message: string
}
