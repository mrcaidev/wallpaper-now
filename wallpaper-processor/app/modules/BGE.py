from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import csv
from sklearn.metrics.pairwise import cosine_similarity
import os
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)

class BGEEmbedder:
    def __init__(self):
        # 获取绝对路径 + 转为 POSIX 格式
        model_path = (Path(__file__).resolve().parent / "../../models/bge_model").resolve()

        # Debug 输出确认路径
        if not model_path.exists():
            raise FileNotFoundError(f"❌ 模型路径不存在: {model_path}")

        # 尝试加载本地模型
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
        self.model = AutoModel.from_pretrained(str(model_path), local_files_only=True)

    def encode(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0]
            embeddings = torch.nn.functional.normalize(embeddings,p=2, dim=-1)
        return embeddings.squeeze(0)

def main():
    bgeEmbedder = BGEEmbedder()

    descriptions = []
    with open("data/image_infos.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            descriptions.append(row["description"])
            # descriptions.append(row)

    # 得到每个描述的句向量（768维）
    embeddings = np.array([bgeEmbedder.encode(desc).cpu().numpy() for desc in descriptions])

    path = "data/text_embeddings.npy"
    if os.path.exists(path):
        old = np.load(path)
        combined = np.vstack([old, embeddings])
    else:
        combined = embeddings
    np.save(path, combined)


if __name__ == "__main__":
    main()