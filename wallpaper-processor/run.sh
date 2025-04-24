docker run --rm \
  --network=wallpaper-now_default \
  --env-file .env \
  -v ${PWD}/models:/app/models \
  wallpaper-vectorizer
