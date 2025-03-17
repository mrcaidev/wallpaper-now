declare module "bun" {
  interface Env {
    POSTGRES_URL: string;
    JWT_SECRET: string;
    KAFKA_BROKERS: string;
  }
}
