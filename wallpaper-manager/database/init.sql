create table if not exists wallpapers (
  id uuid default gen_random_uuid() primary key,
  description text not null,
  width integer not null,
  height integer not null,
  small_url text not null,
  regular_url text not null,
  raw_url text not null,
  deduplication_key text not null unique
);
