declare module "bun" {
  interface Env {
    API_KEY: string;
    POSTGRES_URL: string;
    KAFKA_BROKERS: string;
  }
}
