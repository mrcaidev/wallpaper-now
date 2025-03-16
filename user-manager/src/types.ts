export type PrivateUser = {
  id: string;
  username: string;
  createdAt: string;
  passwordHash: string;
  passwordSalt: string;
};

export type PublicUser = Omit<PrivateUser, "passwordHash" | "passwordSalt">;
