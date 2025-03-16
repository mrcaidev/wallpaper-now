import { sign, verify } from "hono/jwt";

export class JwtError extends Error {
  constructor(message?: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "JwtError";
  }
}

type Payload = {
  id: string;
};

const secretKey = Bun.env.JWT_SECRET_KEY;

export async function signJwt(payload: Payload) {
  try {
    return await sign(payload, secretKey);
  } catch (error) {
    throw new JwtError("Failed to sign token", { cause: error });
  }
}

export async function verifyJwt(token: string) {
  try {
    const { id } = await verify(token, secretKey);
    return { id } as Payload;
  } catch (error) {
    throw new JwtError("Invalid token", { cause: error });
  }
}
