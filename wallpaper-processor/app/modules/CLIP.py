import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
from io import BytesIO
from urllib.parse import urlparse
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)
def is_url(path):
    return urlparse(path).scheme in ('http', 'https')

def load_image(path_or_url):
    if is_url(path_or_url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(path_or_url, headers=headers)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    else:
        return Image.open(path_or_url).convert("RGB")


class CLIPEmbedder:
    def __init__(self):
        pass
        # 1. 初始化模型（推荐 Chinese-CLIP ViT-B/16）
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_path = (Path(__file__).resolve().parent / "../../models/clip_model").resolve()

        # Debug 输出确认路径
        if not model_path.exists():
            raise FileNotFoundError(f"❌ 模型路径不存在: {model_path}")
        

        # 尝试加载本地模型
        self.model = CLIPModel.from_pretrained(model_path).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_path)

    # 2. 图片向量提取函数
    def encode(self, image_path: str):
        image = load_image(image_path)
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
        return image_features.squeeze(0)  # shape: (512,) or (768,)
    
    def get_text_features(self, description):
        inputs = self.processor(description, return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)
        return text_features.squeeze(0)  # shape: (512,) or (768,)



# 4. 示例运行
if __name__ == "__main__":
    clipEmbedder = CLIPEmbedder()

    folder = "./wallpapers"  # 你的壁纸图片文件夹路径
    base_path = "./data/wallpapers/{:04d}.jpg"

    image_paths = [base_path.format(num) for num in range(0, 3854)]

    embeddings = np.array([clipEmbedder.encode(image_path).cpu().numpy() for image_path in image_paths])

    np.save("./data/image_embeddings.npy", embeddings)
    



