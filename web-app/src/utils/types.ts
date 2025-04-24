export type User = {
  id: string;
  username: string;
  createdAt: string;
};

export type Wallpaper = {
  id: string;
  description: string;
  width: number;
  height: number;
  smallUrl: string;
  regularUrl: string;
  rawUrl: string;
  attitude: "liked" | "disliked" | null;
};
