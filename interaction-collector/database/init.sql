create table if not exists interactions (
  user_id uuid not null,
  wallpaper_id uuid not null,
  liked_at timestamptz default null,
  disliked_at timestamptz default null,
  downloaded_at timestamptz default null,
  primary key (user_id, wallpaper_id),
  check (liked_at is null or disliked_at is null)
);
