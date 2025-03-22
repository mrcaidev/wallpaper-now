class Semaphore {
  private count: number;
  private queue: (() => void)[];

  public constructor(count = 1) {
    this.count = count;
    this.queue = [];
  }

  public async acquire() {
    return new Promise<void>((resolve) => {
      this.count--;
      if (this.count >= 0) {
        resolve();
      } else {
        this.queue.push(resolve);
      }
    });
  }

  public release() {
    this.count++;
    this.queue.shift()?.();
  }
}

async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

type Options = {
  limit?: number;
  interval?: number;
};

export async function parallel<T>(
  tasks: (() => Promise<T>)[],
  options: Options = {},
) {
  const { limit = 5, interval = 1000 } = options;

  const results = Array<T>(tasks.length);
  let count = 0;

  const semaphore = new Semaphore(limit);

  return new Promise<T[]>((resolve) => {
    for (const [i, task] of tasks.entries()) {
      semaphore
        .acquire()
        .then(() => task())
        .then((value) => {
          results[i] = value;
        })
        .then(() => sleep(interval))
        .finally(() => {
          semaphore.release();
          count++;
          if (count === tasks.length) {
            resolve(results);
          }
        });
    }
  });
}
