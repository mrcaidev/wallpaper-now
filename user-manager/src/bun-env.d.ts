declare module "bun" {
  interface Env {
    PORT?: number;
    POSTGRES_URL: string;
    JWT_SECRET_KEY: string;
    KAFKA_BROKERS: string;
  }
}
