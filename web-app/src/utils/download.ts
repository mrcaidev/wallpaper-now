import { toast } from "sonner";

export async function download(url: string, filename: string) {
  try {
    const res = await fetch(url);

    if (!res.ok) {
      toast.error("Download failed");
      return;
    }

    const extension = res.headers.get("Content-Type")?.split("/")[1] || "jpg";

    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = `${filename}.${extension}`;

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(blobUrl);
  } catch (error) {
    toast.error(error instanceof Error ? error.message : "Download failed");
  }
}
