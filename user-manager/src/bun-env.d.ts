declare module "bun" {
  interface Env {
    PORT?: number;
    POSTGRES_URL: string;
    JWT_SECRET: string;
    KAFKA_BROKERS: string;
  }
}
