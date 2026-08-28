export interface Service {
  name: string;
  image: string;
  ports: string[];
  depends_on: string[];
  networks: string[];
  volumes: string[];
  environment: Record<string, string>;
  healthcheck: Record<string, unknown> | null;
}

export interface Project {
  id: string;
  name: string;
  path: string;
  compose_file: string;
  services: Service[];
  networks: string[];
}
