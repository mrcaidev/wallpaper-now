import { devSleep } from "@/utils/dev.ts";
import type { Wallpaper } from "@/utils/types";
import { useInfiniteQuery, useQuery } from "@tanstack/react-query";

const mockWallpapers: Wallpaper[] = [
  {
    id: "ac70da2e-afdf-4e3a-8386-91e2ce3c11ab",
    description: "A large body of water with mountains in the background",
    previewUrl:
      "https://images.unsplash.com/photo-1740715537042-6de862cdaab4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQyMDAzMTkwfA&ixlib=rb-4.0.3&q=80&w=1080",
    originalUrl:
      "https://images.unsplash.com/photo-1740715537042-6de862cdaab4?ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQxOTk5MzM1fA&ixlib=rb-4.0.3",
    width: 2477,
    height: 3715,
    attitude: "liked",
    score: 364,
  },
  {
    id: "804f140d-44bb-4c2a-9a2e-3e0431a159ef",
    description: "A view of a mountain range with a star trail in the sky",
    previewUrl:
      "https://images.unsplash.com/photo-1720811119383-96f0dade1e04?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQyMDA0MTE2fA&ixlib=rb-4.0.3&q=80&w=1080",
    originalUrl:
      "https://images.unsplash.com/photo-1720811119383-96f0dade1e04?ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQxOTk5NDY5fA&ixlib=rb-4.0.3",
    width: 5472,
    height: 3420,
    attitude: "disliked",
    score: 302,
  },
  {
    id: "c0f2feef-7502-4915-aab5-8643930e867e",
    description: "A mountain covered in clouds at sunset",
    previewUrl:
      "https://images.unsplash.com/photo-1735558427078-43aa416a3145?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQyMDA0MTMzfA&ixlib=rb-4.0.3&q=80&w=1080",
    originalUrl:
      "https://images.unsplash.com/photo-1735558427078-43aa416a3145?ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQxOTk5NjA5fA&ixlib=rb-4.0.3",
    width: 8640,
    height: 5760,
    attitude: null,
    score: 237,
  },
  {
    id: "c894eb5f-59f6-408a-9ae1-e500e62c7c59",
    description:
      "努沙佩尼达岛的破碎海滩, 巴厘岛, 印度尼西亚 (© joakimbkk/Getty Images)",
    previewUrl:
      "https://cdn.wallpaperhub.app/cloudcache/8/2/e/f/7/4/82ef744332152dab1bd32baffdb68d2f65152bd6.jpg",
    originalUrl:
      "https://cdn.wallpaperhub.app/cloudcache/9/9/2/2/9/3/992293f3311bdc3104d53100f01c9539b99158cf.jpg",
    width: 3840,
    height: 2160,
    attitude: null,
    score: 214,
  },
  {
    id: "1b92771e-4565-431b-9934-674c89df96e0",
    description: "green leafed tree on body of water under starry sky",
    previewUrl:
      "https://images.unsplash.com/photo-1502318217862-aa4e294ba657?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQyMDA0MTUxfA&ixlib=rb-4.0.3&q=80&w=1080",
    originalUrl:
      "https://images.unsplash.com/photo-1502318217862-aa4e294ba657?ixid=M3wxMjA3fDB8MXxhbGx8fHx8fHx8fHwxNzQxOTk5NzczfA&ixlib=rb-4.0.3",
    width: 2143,
    height: 3000,
    attitude: null,
    score: 189,
  },
];

export function useTrendingQuery() {
  return useQuery<Wallpaper[]>({
    queryKey: ["trending"],
    queryFn: async () => {
      await devSleep(1000);
      return mockWallpapers.slice(0, 5);
    },
  });
}

export function useRecommendationQuery() {
  return useInfiniteQuery<Wallpaper[]>({
    queryKey: ["recommendation"],
    queryFn: async () => {
      await devSleep(1000);
      return mockWallpapers;
    },
    getNextPageParam: () => true,
    initialPageParam: true,
  });
}
