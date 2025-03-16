import { Kafka, logLevel } from "kafkajs";
import type { PublicUser } from "./types.ts";

const kafka = new Kafka({
  clientId: "user-manager",
  brokers: Bun.env.KAFKA_BROKERS.split(","),
  logLevel: logLevel.ERROR,
});
console.log("Initialized Kafka client");

const admin = kafka.admin();
await admin.connect();
console.log("Connected admin to Kafka");

const topicsCreated = await admin.createTopics({
  topics: [
    {
      topic: "UserCreated",
      numPartitions: 3,
    },
  ],
});
if (topicsCreated) {
  console.log("Created topics");
} else {
  console.log("Topics already exist");
}

const producer = kafka.producer();
await producer.connect();
console.log("Connected producer to Kafka");

export async function sendUserCreatedEvent(payload: PublicUser) {
  const [record] = await producer.send({
    topic: "UserCreated",
    messages: [{ value: JSON.stringify(payload) }],
  });
  console.log("Sent event:", JSON.stringify(record));
}

for (const errorType of ["unhandledRejection", "uncaughtException"]) {
  process.on(errorType, async (error) => {
    console.error(error);
    try {
      await admin.disconnect();
      console.log("Disconnected admin from Kafka");
      await producer.disconnect();
      console.log("Disconnected producer from Kafka");

      process.exit(0);
    } catch {
      process.exit(1);
    }
  });
}

for (const signal of ["SIGTERM", "SIGINT", "SIGUSR2"]) {
  process.once(signal, async () => {
    try {
      await admin.disconnect();
      console.log("Disconnected admin from Kafka");
      await producer.disconnect();
      console.log("Disconnected producer from Kafka");
    } finally {
      process.kill(process.pid, signal);
    }
  });
}
