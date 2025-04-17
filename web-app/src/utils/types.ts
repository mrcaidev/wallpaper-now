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
  previewUrl: string;
  originalUrl: string;
  attitude: "liked" | "disliked" | null;
  score: number;
};
