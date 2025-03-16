import type { Wallpaper } from "@/types.ts";
import { useMemo } from "react";
import { useMediaQuery } from "./use-media-query.ts";

export function useWallpaperColumns(wallpapers: Wallpaper[]) {
  const lg = useMediaQuery("(min-width: 1024px)");
  const sm = useMediaQuery("(min-width: 640px)");
  const columnCount = lg ? 3 : sm ? 2 : 1;

  return useMemo(() => {
    const columns = Array.from(
      { length: columnCount },
      () => [] as Wallpaper[],
    );
    const heights = Array(columnCount).fill(0);

    for (const wallpaper of wallpapers) {
      const { width, height } = wallpaper;
      const lowestIndex = heights.indexOf(Math.min(...heights));
      columns[lowestIndex]?.push(wallpaper);
      heights[lowestIndex] += height / width;
    }

    return columns;
  }, [wallpapers, columnCount]);
}
