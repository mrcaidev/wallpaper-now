import type { Wallpaper } from "@/types.ts";
import { sql } from "bun";

type WallpaperInput = Omit<Wallpaper, "id"> & { deduplicationKey: string };

export async function persist(inputs: WallpaperInput[]) {
  if (inputs.length === 0) {
    return [];
  }

  const snakeCaseInputs = inputs.map((i) => ({
    description: i.description,
    width: i.width,
    height: i.height,
    small_url: i.smallUrl,
    regular_url: i.regularUrl,
    raw_url: i.rawUrl,
    deduplication_key: i.deduplicationKey,
  }));

  const outputs = await sql`
    insert into wallpapers ${sql(snakeCaseInputs)}
    on conflict (deduplication_key) do nothing
    returning
      id,
      description,
      width,
      height,
      small_url as "smallUrl",
      regular_url as "regularUrl",
      raw_url as "rawUrl"`;
  return outputs as Wallpaper[];
}
