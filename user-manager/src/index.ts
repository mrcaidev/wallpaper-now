import { sql } from "bun";
import { type Context, Hono } from "hono";
import { deleteCookie, getCookie, setCookie } from "hono/cookie";
import { HTTPException } from "hono/http-exception";
import { logger } from "hono/logger";
import { validator } from "hono/validator";
import { JwtError, signJwt, verifyJwt } from "./jwt.ts";
import { sendUserCreatedEvent } from "./kafka.ts";
import {
  generatePasswordSalt,
  hashPassword,
  verifyPassword,
} from "./password.ts";
import type { PrivateUser, PublicUser } from "./types.ts";

const app = new Hono();

app.use(logger());

app.get("/", (c) => {
  return c.text("ok");
});

app.get("/me", async (c) => {
  const token = getCookie(c, "token");

  if (!token) {
    throw new HTTPException(401, { message: "Please log in first" });
  }

  const { id } = await verifyJwt(token);

  const rows = await sql`
    select id, username, created_at as "createdAt"
    from users
    where id = ${id}`;
  const user = rows[0] as PublicUser | undefined;

  if (!user) {
    deleteCookie(c, "token");
    throw new HTTPException(401, { message: "Invalid token" });
  }

  return c.json(user);
});

app.post(
  "/login",
  validator("json", (json) => {
    const { username, password } = json;

    if (!username || typeof username !== "string") {
      throw new HTTPException(400, { message: "Username is required" });
    }

    if (!password || typeof password !== "string") {
      throw new HTTPException(400, { message: "Password is required" });
    }

    return { username, password };
  }),
  async (c) => {
    const { username, password } = c.req.valid("json");

    const existingRows = await sql`
      select
        id,
        username,
        created_at as "createdAt",
        password_hash as "passwordHash",
        password_salt as "passwordSalt"
      from users
      where username = ${username}`;
    const user = existingRows[0] as PrivateUser | undefined;

    if (user) {
      const { id, username, createdAt, passwordHash, passwordSalt } = user;

      const verified = await verifyPassword(
        password,
        passwordSalt,
        passwordHash,
      );

      if (!verified) {
        throw new HTTPException(401, { message: "Wrong password" });
      }

      const token = await signJwt({ id });
      setCookie(c, "token", token, { httpOnly: true });

      return c.json({ id, username, createdAt }, 201);
    }

    const passwordSalt = generatePasswordSalt();
    const passwordHash = await hashPassword(password, passwordSalt);

    const insertedRows = await sql`
      insert into users (username, password_hash, password_salt)
      values (${username}, ${passwordHash}, ${passwordSalt})
      returning id, username, created_at as "createdAt"`;
    const newUser = insertedRows[0] as PublicUser;

    await sendUserCreatedEvent(newUser);

    const token = await signJwt({ id: newUser.id });
    setCookie(c, "token", token, { httpOnly: true });

    return c.json(newUser, 201);
  },
);

app.post("/logout", async (c) => {
  deleteCookie(c, "token");
  return c.body(null, 204);
});

app.onError((error: unknown, c: Context) => {
  if (error instanceof JwtError) {
    deleteCookie(c, "token");
    return c.json({ error: "Login expired. Please log in again" }, 401);
  }

  if (error instanceof HTTPException) {
    return c.json({ error: error.message }, error.status);
  }

  console.error(error);
  return c.json({ error: "Server error" }, 500);
});

export default app;
