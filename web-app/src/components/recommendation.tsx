import { useRecommendationQuery } from "@/api/wallpaper.ts";
import { useInfiniteScroll } from "@/hooks/use-infinite-scroll.ts";
import { useMediaQuery } from "@/hooks/use-media-query.ts";
import type { Wallpaper } from "@/utils/types.ts";
import { Loader2Icon } from "lucide-react";
import { useMemo, useRef } from "react";
import { Skeleton } from "./ui/skeleton.tsx";
import { WallpaperCard } from "./wallpaper-card.tsx";

export function Recommendation() {
  return (
    <section className="p-6">
      <h2 className="mb-6 text-xl sm:text-3xl font-bold">
        👍 Recommended for You
      </h2>
      <Masonry />
    </section>
  );
}

function Masonry() {
  const {
    data: wallpapers,
    isPending,
    error,
    fetchNextPage,
  } = useRecommendationQuery();
  const columns = useWallpaperColumns(wallpapers ?? []);

  if (isPending) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="space-y-4">
          <Skeleton className="aspect-video" />
          <Skeleton className="aspect-square" />
        </div>
        <div className="hidden sm:block space-y-4">
          <Skeleton className="aspect-square" />
          <Skeleton className="aspect-video" />
        </div>
        <div className="hidden lg:block space-y-4">
          <Skeleton className="aspect-video" />
          <Skeleton className="aspect-square" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-72 p-4 border rounded-md">
        <p className="max-w-md text-muted-foreground text-sm text-center text-balance">
          Oops! We can&apos;t seem to retrieve recommended wallpapers now 😢
          What about try again later?
        </p>
      </div>
    );
  }

  if (wallpapers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-72 p-4 border rounded-md">
        <p className="max-w-md text-muted-foreground text-sm text-center text-balance">
          Well... Why nothing here? 🤔 Seems like something has gone wrong in
          our system. Please check back later!
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {columns.map((column, index) => (
          <div key={`${columns.length}.${index}`} className="space-y-4">
            {column.map((wallpaper, index) => (
              <WallpaperCard
                key={`${wallpaper.id}.${index}`}
                wallpaper={wallpaper}
              />
            ))}
          </div>
        ))}
      </div>
      <LoadTrigger load={fetchNextPage} />
    </>
  );
}

function useWallpaperColumns(wallpapers: Wallpaper[]) {
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
      const lowestIndex = heights.indexOf(Math.min(...heights));
      columns[lowestIndex]?.push(wallpaper);
      heights[lowestIndex] += wallpaper.height / wallpaper.width;
    }

    return columns;
  }, [wallpapers, columnCount]);
}

function LoadTrigger({ load }: { load: () => void }) {
  const triggerRef = useRef<HTMLDivElement>(null);
  useInfiniteScroll(triggerRef, load);

  return (
    <div
      ref={triggerRef}
      className="flex items-center justify-center gap-2 my-4 text-sm"
    >
      <Loader2Icon size={14} className="animate-spin" />
      Loading more for you...
    </div>
  );
}
