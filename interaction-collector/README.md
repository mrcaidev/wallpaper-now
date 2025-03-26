# Interaction Collector

Collects user interactions with wallpapers.

## Responsibilities

- Provides an external API to collect user interactions.
- Provides an internal API to retrieve a user's attitudes towards multiple wallpapers.
- Determines the weight of interactions.

## Events

### InteractionCollected

A user interaction has been collected.

```json
{
  "userId": "e4cc007f-c98b-464e-8641-a1ed28067ac6",
  "wallpaperId": "d1ea2c22-36f9-4b46-ba0d-ba5c8f1c3b6e",
  "weight": 3,
  "collectedAt": "2025-03-26T02:09:27.509Z"
}
```

- `userId`: Who is interacting with the wallpaper.
- `wallpaperId`: Which wallpaper he/she is interacting with.
- `weight`: The weight difference between the previous interaction and the current one.
- `collectedAt`: ISO 8601 representation of when the interaction is collected.

> Caution:
>
> The `weight` field is NOT the weight of the interaction itself.
>
> For example: if a user has previously liked a wallpaper, but now dislikes it, the `weight` field should be -6, which is the difference between like (+3) and dislike (-3).
