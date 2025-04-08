CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE user_profiles (
    user_id UUID NOT NULL PRIMARY KEY,
    preference_vector VECTOR(768) NOT NULL,
    norm_preference_vector VECTOR(768) NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL
);

CREATE TABLE wallpaper_embedding (
    wallpaper_id UUID NOT NULL PRIMARY KEY,
    embedding VECTOR(768) NOT NULL,
    norm_embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE recommend_history (
    id UUID NOT NULL PRIMARY KEY,
    user_id UUID NOT NULL,
    wallpaper_id UUID NOT NULL,
    recommendAt TIMESTAMPTZ NOT NULL
);