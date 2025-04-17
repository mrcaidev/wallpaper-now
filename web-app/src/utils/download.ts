import { toast } from "sonner";

export async function downloadImage(url: string, filename: string) {
  try {
    const res = await fetch(url);

    if (!res.ok) {
      toast.error("Failed to download", { description: res.statusText });
    }

    const contentType = res.headers.get("Content-Type") || "";

    if (!contentType.startsWith("image/")) {
      toast.error("Failed to download", {
        description: "This URL does not point to an image",
      });
    }

    const extension = contentType.split("/")[1] || "jpg";

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
    const reason = error instanceof Error ? error.message : "Unknown error";
    toast.error("Failed to download", { description: reason });
  }
}
