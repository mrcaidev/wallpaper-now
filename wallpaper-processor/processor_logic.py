from app.modules.BGE import BGEEmbedder
from app.modules.CLIP import CLIPEmbedder
from app.modules.MLP import ImageTextFusion
import torch
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from app.utils.logger import get_logger

logger = get_logger(__name__)
bgeEmbedder = BGEEmbedder()
clipEmbedder = CLIPEmbedder()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

current_dir = Path(__file__).resolve().parent
fusion_model_path = (current_dir / "./models/fusion_mlp_triplet.pt").resolve()

fusion_model = ImageTextFusion().to(device)
fusion_model.load_state_dict(torch.load(fusion_model_path, map_location=device))
fusion_model.eval()

# === 处理逻辑 ===
def process_one(wallpaper):
    try:
        image_path = wallpaper['smallUrl']
        text_path = wallpaper['description']
        image_id = wallpaper['id']

        # === 向量化处理 ===
        image_vec = clipEmbedder.encode(image_path=image_path).to(device)
        text_vec = bgeEmbedder.encode(text=text_path).to(device)

        image_vec = image_vec.unsqueeze(0)  # [D1] → [1, D1]
        text_vec = text_vec.unsqueeze(0)    # [D2] → [1, D2]

        fused_vec = fusion_model(image_vec, text_vec)  # 输出：[1, D]
        fused_np = fused_vec.detach().cpu().numpy().squeeze(0)  # 去掉 batch 维度，变成 [D]

        return {"id": image_id, "embedding": fused_np.tolist()}
    except Exception as e:
        logger.info(f"❌ 出现异常：{e}")
        return None

def process_wallpaper(wallpaper_message):
    wallpapers = wallpaper_message['wallpapers']

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(process_one, wallpapers))
    return [r for r in results if r is not None]
