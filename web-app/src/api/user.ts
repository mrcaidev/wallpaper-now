import type { User } from "@/utils/types.ts";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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

  return useMutation<User & { token: string }, Error, FormData>({
    mutationFn: async (formData) => {
      const { username, password } = Object.fromEntries(formData);
      if (!username || !password) {
        throw new Error("Username and password are required");
      }
      return await request.post("/login", { username, password });
    },
    onSuccess: ({ token, ...me }) => {
      localStorage.setItem("token", token);

      queryClient.cancelQueries({ queryKey: ["me"] });
      queryClient.setQueryData(["me"], me);
    },
  });
}

export function useLogOutMutation() {
  const queryClient = useQueryClient();

  return () => {
    localStorage.removeItem("token");

    queryClient.cancelQueries({ queryKey: ["me"] });
    queryClient.resetQueries({ queryKey: ["me"] });
  };
}
