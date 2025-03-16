export function devLog(...args: Parameters<typeof console.log>) {
  if (!import.meta.env.DEV) {
    return;
  }
  console.log(`[${new Date().toLocaleTimeString()}]`, ...args);
}

export async function devSleep(ms: number) {
  if (!import.meta.env.DEV) {
    return;
  }
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
