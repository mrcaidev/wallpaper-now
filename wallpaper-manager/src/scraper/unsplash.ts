import type { Wallpaper } from "@/types.ts";
import { parallel } from "./parallel.ts";
import { persist } from "./persist.ts";

type UnsplashWallpaper = {
  id: string;
  width: number;
  height: number;
  description: string;
  alt_description: string;
  urls: {
    raw: string;
    regular: string;
    small: string;
  };
  premium: boolean;
  plus: boolean;
};

export async function scrapeUnsplash(total: number) {
  const pages = paginate(total);
  const scrapeResults = await parallel(
    pages.map((p) => () => scrapePage(p.page, p.pageSize)),
  );
  const wallpapers = scrapeResults.flat().filter(Boolean);
  console.log(`[Unsplash] Finished. Scraped ${wallpapers.length} in total`);
  return wallpapers;
}

function paginate(total: number) {
  const MAX_PAGE_SIZE = 30;
  const fullPageCount = Math.floor(total / MAX_PAGE_SIZE);
  const remainder = total % MAX_PAGE_SIZE;

  const pages = Array.from({ length: fullPageCount }, (_, i) => ({
    page: i + 1,
    pageSize: MAX_PAGE_SIZE,
  }));

  if (remainder > 0) {
    pages.push({ page: fullPageCount + 1, pageSize: remainder });
  }

  return pages;
}

async function scrapePage(page: number, pageSize: number) {
  const res = await fetch(
    `https://unsplash.com/napi/topics/wallpapers/photos?page=${page}&per_page=${pageSize}`,
  );
  const data = (await res.json()) as UnsplashWallpaper[];

  const wallpapers = data
    .filter((w) => !w.premium && !w.plus)
    .map(
      (w) =>
        ({
          id: crypto.randomUUID(),
          description: w.alt_description || w.description || "",
          width: w.width,
          height: w.height,
          smallUrl: w.urls.small,
          regularUrl: w.urls.regular,
          rawUrl: w.urls.raw,
          deduplicationKey: `unsplash:${w.id}`,
        }) as Wallpaper,
    );
  const persistedCount = await persist(wallpapers);

  console.log(
    `[Unsplash] Scraped page ${page}, expect ${pageSize}, got ${wallpapers.length}, persisted ${persistedCount}`,
  );

  return wallpapers;
}
