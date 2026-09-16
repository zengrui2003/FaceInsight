from __future__ import annotations

import base64
import time
from collections.abc import Callable
from pathlib import Path

from aip import AipFace

from .config import BaiduConfig


MAX_IMAGE_SIZE = 10 * 1024 * 1024
RETRYABLE_ERROR_CODES = {18, "SDK108"}


class FaceAnalyzer:
    def __init__(self, config: BaiduConfig, request_interval: float = 1.1):
        self.client = AipFace(config.app_id, config.api_key, config.secret_key)
        self.request_interval = request_interval

    @staticmethod
    def encode_image(path: Path) -> str:
        if path.stat().st_size > MAX_IMAGE_SIZE:
            raise ValueError(f"图片超过 10MB，百度接口无法处理：{path.name}")
        content = base64.b64encode(path.read_bytes()).decode("utf-8")
        return content

    def detect(self, path: Path) -> dict:
        options = {"face_field": "age,expression,beauty"}
        return self.client.detect(self.encode_image(path), "BASE64", options)

    def detect_score(self, path: Path, max_retries: int = 4) -> int:
        """返回 0 表示未检测到人脸，1-10 表示颜值分段。"""
        response = self.detect(path)
        error_code = response.get("error_code", 0)
        retries = 0
        while error_code in RETRYABLE_ERROR_CODES and retries < max_retries:
            time.sleep(2.0 * (retries + 1))
            response = self.detect(path)
            error_code = response.get("error_code", 0)
            retries += 1
        if error_code != 0:
            if error_code in {222202, 222203, 222204}:
                return 0
            message = response.get("error_msg", "未知错误")
            raise RuntimeError(f"百度检测失败（{error_code}）：{message}")

        faces = response.get("result", {}).get("face_list", [])
        if not faces:
            return 0

        beauty = float(faces[0].get("beauty", 0))
        if beauty <= 0:
            return 0
        return min(10, max(1, int(beauty // 10) + 1))

    def analyze_images(
        self,
        paths: list[Path],
        progress: Callable[[int, int, Path], None] | None = None,
    ) -> list[int]:
        scores: list[int] = []
        for index, path in enumerate(paths, start=1):
            scores.append(self.detect_score(path))
            if progress:
                progress(index, len(paths), path)
            if index < len(paths):
                time.sleep(self.request_interval)
        return scores


def aggregate_scores(scores: list[int]) -> list[int]:
    """score_counts[0] 是无人脸数量，score_counts[1] 到 [10] 是 1 到 10 分数量。"""
    score_counts = [0] * 11
    for score in scores:
        score_counts[score] += 1
    return score_counts
