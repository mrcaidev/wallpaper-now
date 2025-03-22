import type { Page } from "./paginate.ts";
import { persist } from "./persist.ts";

type HubWallpaper = {
  id: string;
  description: string;
  variations: {
    resolutions: {
      width: number;
      height: number;
      resolutionLabel: string;
      url: string;
    }[];
  }[];
};

export async function scrapeHubPage(page: Page) {
  const res = await fetch(
    `https://wallpaperhub.app/api/v1/wallpapers?page=${page.index}&limit=${page.size}`,
  );
  const data = (await res.json()) as { entities: { entity: HubWallpaper }[] };

  const wallpapers = data.entities.map(({ entity: w }) => ({
    description: w.description,
    width: w.variations[0]?.resolutions[0]?.width ?? 3840,
    height: w.variations[0]?.resolutions[0]?.height ?? 2160,
    smallUrl: w.variations[0]?.resolutions.at(-1)?.url ?? "",
    regularUrl:
      w.variations[0]?.resolutions.find(
        (r) => r.height === 1080 || r.resolutionLabel === "1080p",
      )?.url ?? "",
    rawUrl: w.variations[0]?.resolutions[0]?.url ?? "",
    deduplicationKey: `hub:${w.id}`,
  }));
  const deduplicatedWallpapers = await persist(wallpapers);

  console.log(
    `[Hub] Scraped page ${page.index}, expect ${page.size}, got ${wallpapers.length}, persisted ${deduplicatedWallpapers.length}`,
  );

  return deduplicatedWallpapers;
}
