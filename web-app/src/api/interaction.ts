import { useMutation } from "@tanstack/react-query";
import { request } from "./request.ts";

export function useInteractionMutation() {
  return useMutation<
    void,
    Error,
    { wallpaperId: string; action: "like" | "dislike" | "download" }
  >({
    mutationFn: async (variables) => {
      await request.post("/interactions", variables);
    },
  });
}
