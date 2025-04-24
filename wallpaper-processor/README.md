# Wallpaper Processor


The wallpaper processor is designed to convert input values into vector representations.

## Responsibility


* Mapping scraped images and their associated metadata into a shared vision-language embedding space
* Vectorizing user-provided search queries to enable semantic similarity matching


## Events

### WallpaperVectorized

A batch of wallpapers and their infos has been vectorized.

```json
[
    {
    "id": "03c7d4d2-cc77-4882-9d76-ad32fbfa23bf", 
    "embedding": [] // [768]
    },
    {
    "id": "72dda60f-29f2-4796-8ac9-5c600a6b5d41", 
    "embedding": [] // [768]
    },
]
```