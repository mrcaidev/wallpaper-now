import {
  useDislikeMutation,
  useDownloadMutation,
  useLikeMutation,
} from "@/api/interaction.ts";
import { useMeQuery } from "@/api/user.ts";
import type { Wallpaper } from "@/types.ts";
import { downloadImage } from "@/utils/download.ts";
import {
  DownloadIcon,
  EyeOffIcon,
  ThumbsDownIcon,
  ThumbsUpIcon,
} from "lucide-react";
import { type Dispatch, type SetStateAction, useState } from "react";
import { Button } from "./ui/button.tsx";
import { cn } from "./ui/utils.ts";

type Props = {
  wallpaper: Wallpaper;
  imgClassname?: string;
};

export function WallpaperCard({ wallpaper, imgClassname = "" }: Props) {
  const [attitude, setAttitude] = useState(wallpaper.attitude);

  return (
    <div className="group relative rounded-md overflow-hidden">
      <img
        src={wallpaper.previewUrl}
        alt={wallpaper.description}
        loading="lazy"
        decoding="async"
        className={imgClassname}
      />
      {attitude === "disliked" && (
        <div className="flex flex-col items-center justify-center gap-1 absolute inset-0 backdrop-blur-md">
          <EyeOffIcon />
          <p className="text-sm">Blurred as disliked</p>
        </div>
      )}
      <div className="flex flex-col justify-between invisible group-hover:visible absolute inset-0 p-3 bg-gradient-to-b from-transparent group-hover:from-zinc-950/50 via-transparent group-hover:via-zinc-950/20 to-transparent group-hover:to-zinc-950/50 transition-colors">
        <div className="flex items-center justify-end gap-2">
          <LikeButton
            wallpaper={wallpaper}
            attitude={attitude}
            setAttitude={setAttitude}
          />
          <DislikeButton
            wallpaper={wallpaper}
            attitude={attitude}
            setAttitude={setAttitude}
          />
        </div>
        <div className="flex items-end justify-between gap-2">
          <p className="text-zinc-50 text-sm capitalize text-balance line-clamp-2">
            {wallpaper.description}
          </p>
          <DownloadButton wallpaper={wallpaper} />
        </div>
      </div>
    </div>
  );
}

type AttitudeButtonProps = {
  wallpaper: Wallpaper;
  attitude: Wallpaper["attitude"];
  setAttitude: Dispatch<SetStateAction<Wallpaper["attitude"]>>;
};

function LikeButton({ wallpaper, attitude, setAttitude }: AttitudeButtonProps) {
  const { data: me } = useMeQuery();

  const { mutate } = useLikeMutation(wallpaper.id);

  if (!me) {
    return null;
  }

  const handleClick = () => {
    const oldAttitude = attitude;

    setAttitude((attitude) => (attitude === "liked" ? null : "liked"));

    mutate(undefined, {
      onError: () => {
        setAttitude(oldAttitude);
      },
    });
  };

  return (
    <Button
      variant="secondary"
      size="icon"
      onClick={handleClick}
      aria-label="Like this wallpaper"
      className="shrink-0"
    >
      <ThumbsUpIcon className={cn(attitude === "liked" && "fill-amber-300")} />
    </Button>
  );
}

function DislikeButton({
  wallpaper,
  attitude,
  setAttitude,
}: AttitudeButtonProps) {
  const { data: me } = useMeQuery();

  const { mutate } = useDislikeMutation(wallpaper.id);

  if (!me) {
    return null;
  }

  const handleClick = () => {
    const oldAttitude = attitude;

    setAttitude((attitude) => (attitude === "disliked" ? null : "disliked"));

    mutate(undefined, {
      onError: () => {
        setAttitude(oldAttitude);
      },
    });
  };

  return (
    <Button
      variant="secondary"
      size="icon"
      onClick={handleClick}
      aria-label="Dislike this wallpaper"
      className="shrink-0"
    >
      <ThumbsDownIcon
        className={cn(attitude === "disliked" && "fill-amber-300")}
      />
    </Button>
  );
}

function DownloadButton({ wallpaper }: { wallpaper: Wallpaper }) {
  const { data: me } = useMeQuery();

  const { mutate } = useDownloadMutation(wallpaper.id);

  const handleClick = async () => {
    if (me) {
      mutate();
    }

    await downloadImage(wallpaper.originalUrl, wallpaper.id);
  };

  return (
    <Button
      variant="secondary"
      size="icon"
      onClick={handleClick}
      aria-label="Download this wallpaper"
      className="shrink-0"
    >
      <DownloadIcon />
    </Button>
  );
}
