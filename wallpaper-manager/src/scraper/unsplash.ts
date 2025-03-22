import type { Page } from "./paginate.ts";
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

export async function scrapeUnsplashPage(page: Page) {
  const res = await fetch(
    `https://unsplash.com/napi/topics/wallpapers/photos?page=${page.index}&per_page=${page.size}`,
  );
  const data = (await res.json()) as UnsplashWallpaper[];

  const wallpapers = data
    .filter((w) => !w.premium && !w.plus)
    .map((w) => ({
      description: w.alt_description || w.description || "",
      width: w.width,
      height: w.height,
      smallUrl: w.urls.small,
      regularUrl: w.urls.regular,
      rawUrl: w.urls.raw,
      deduplicationKey: `unsplash:${w.id}`,
    }));
  const deduplicatedWallpapers = await persist(wallpapers);

  console.log(
    `[Unsplash] Scraped page ${page.index}, expect ${page.size}, got ${wallpapers.length}, persisted ${deduplicatedWallpapers.length}`,
  );

  return deduplicatedWallpapers;
}
