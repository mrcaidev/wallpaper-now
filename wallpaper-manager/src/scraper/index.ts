import { paginate } from "./paginate.ts";
import { parallel } from "./parallel.ts";
import { scrapeUnsplashPage } from "./unsplash.ts";

export const config = [
  {
    source: "Unsplash",
    scrapePage: scrapeUnsplashPage,
    maxPageSize: 30,
    limit: 5,
    interval: 1000,
  },
];

export async function scrape(total: number) {
  const subTotal = Math.ceil(total / config.length);

  const results = await Promise.all(
    config.map(async (c) => {
      const pages = paginate(subTotal, c.maxPageSize);

      const results = await parallel(
        pages.map((p) => () => c.scrapePage(p)),
        { limit: c.limit, interval: c.interval },
      );

      const wallpapers = results.flat().filter(Boolean);

      console.log(
        `[${c.source}] Finished. Scraped ${wallpapers.length} in total`,
      );

      return wallpapers;
    }),
  );

  return results.flat();
}
