import type { Wallpaper } from "@/utils/types";
import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { request } from "./request.ts";

export function useTrendingQuery() {
  return useQuery<Wallpaper[]>({
    queryKey: ["trending"],
    queryFn: async () => {
      return await request.get("/trending");
    },
  });
}

export function useRecommendationQuery() {
  return useInfiniteQuery<Wallpaper[], Error, Wallpaper[]>({
    queryKey: ["recommendation"],
    queryFn: async () => {
      return await request.get("/recommendation");
    },
    select: (data) => data.pages.flat(),
    getNextPageParam: () => true,
    initialPageParam: true,
  });
}
