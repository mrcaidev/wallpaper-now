import type { User } from "@/types.ts";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { request } from "./request.ts";

export function useMeQuery() {
  return useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => {
      return await request.get("/me");
    },
  });
}

export function useLogInMutation() {
  const queryClient = useQueryClient();

  return useMutation<User, Error, FormData>({
    mutationFn: async (formData) => {
      const { username, password } = Object.fromEntries(formData);
      if (!username || !password) {
        throw new Error("Username and password are required");
      }
      return await request.post("/login", { username, password });
    },
    onSuccess: (me) => {
      queryClient.cancelQueries({ queryKey: ["me"] });
      queryClient.setQueryData(["me"], me);
    },
    onError: (error) => {
      toast.error("Failed to log in", { description: error.message });
    },
  });
}

export function useLogOutMutation() {
  const queryClient = useQueryClient();

  return useMutation<void>({
    mutationFn: async () => {
      await request.post("/logout");
    },
    onSuccess: () => {
      queryClient.cancelQueries({ queryKey: ["me"] });
      queryClient.resetQueries({ queryKey: ["me"] });
    },
    onError: (error) => {
      toast.error("Failed to log out", { description: error.message });
    },
  });
}
