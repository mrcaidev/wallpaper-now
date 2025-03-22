import { useMutation } from "@tanstack/react-query";
import { request } from "./request.ts";

export function useLikeMutation(wallpaperId: string) {
  return useMutation<void>({
    mutationFn: async () => {
      await request.post("/interactions", {
        wallpaperId,
        action: "like",
      });
    },
  });
}

export function useDislikeMutation(wallpaperId: string) {
  return useMutation<void>({
    mutationFn: async () => {
      await request.post("/interactions", {
        wallpaperId,
        action: "dislike",
      });
    },
  });
}

export function useDownloadMutation(wallpaperId: string) {
  return useMutation<void>({
    mutationFn: async () => {
      await request.post("/interactions", {
        wallpaperId,
        action: "download",
      });
    },
  });
}
