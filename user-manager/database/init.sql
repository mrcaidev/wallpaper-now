create table if not exists users (
  id uuid default gen_random_uuid() primary key,
  username text not null unique,
  password_hash text not null,
  password_salt text not null,
  created_at timestamptz default now() not null
);
