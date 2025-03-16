import { useTrendingQuery } from "@/apis/wallpaper.ts";
import { Skeleton } from "./ui/skeleton.tsx";
import { WallpaperCard } from "./wallpaper-card.tsx";

export function NowTrending() {
  return (
    <section className="p-6">
      <h2 className="mb-6 text-xl sm:text-3xl font-bold">🔥 Now Trending</h2>
      <HorizontalList />
    </section>
  );
}

function HorizontalList() {
  const { data: wallpapers, isPending, error } = useTrendingQuery();

  if (isPending) {
    return (
      <div className="flex gap-4 pb-6 overflow-hidden">
        <Skeleton className="h-52 aspect-video rounded-md" />
        <Skeleton className="h-52 aspect-video rounded-md" />
        <Skeleton className="h-52 aspect-video rounded-md" />
        <Skeleton className="h-52 aspect-video rounded-md" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-56 p-4 border rounded-md">
        <p className="max-w-md text-muted-foreground text-sm text-center text-balance">
          Oops! We can&apos;t seem to retrieve trending wallpapers now 😢 What
          about try again later?
        </p>
      </div>
    );
  }

  if (wallpapers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-56 p-4 border rounded-md">
        <p className="max-w-md text-muted-foreground text-sm text-center text-balance">
          We haven&apos;t gathered enough data to show trending wallpapers yet
          🤔 Please check back later!
        </p>
      </div>
    );
  }

  return (
    <ul className="flex gap-4 pb-2 overflow-x-auto">
      {wallpapers.map((wallpaper) => (
        <li key={wallpaper.id} className="shrink-0">
          <WallpaperCard wallpaper={wallpaper} imgClassname="h-52" />
        </li>
      ))}
    </ul>
  );
}
