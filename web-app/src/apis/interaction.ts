import { devLog, devSleep } from "@/utils/dev.ts";
import { useMutation } from "@tanstack/react-query";

export function useLikeMutation(wallpaperId: string) {
  return useMutation<void>({
    mutationFn: async () => {
      devLog(`useLikeMutation: ${wallpaperId}`);
      await devSleep(1000);
    },
  });
}

export function useDislikeMutation(wallpaperId: string) {
  return useMutation<void>({
    mutationFn: async () => {
      devLog(`useDislikeMutation: ${wallpaperId}`);
      await devSleep(1000);
    },
  });
}

export function useDownloadMutation(wallpaperId: string) {
  return useMutation<void>({
    mutationFn: async () => {
      devLog(`useDownloadMutation: ${wallpaperId}`);
      await devSleep(1000);
    },
  });
}
