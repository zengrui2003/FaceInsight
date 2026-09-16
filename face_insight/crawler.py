from __future__ import annotations

import re
import shutil
from pathlib import Path

from icrawler.builtin import BingImageCrawler


VALID_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def safe_folder_name(keyword: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", keyword).strip(" ._")
    return name or "unnamed"


def crawl_images(keyword: str, max_num: int, root_dir: Path) -> Path:
    """重新下载指定关键字，避免把上一次的旧图混入统计。"""
    if max_num <= 0:
        raise ValueError("爬取数量必须大于 0。")

    folder = root_dir / safe_folder_name(keyword)
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)

    crawler = BingImageCrawler(
        feeder_threads=2,
        parser_threads=4,
        downloader_threads=8,
        storage={"root_dir": str(folder)},
    )
    crawler.crawl(keyword=keyword, max_num=max_num)
    return folder


def list_images(folder: Path) -> list[Path]:
    files = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VALID_IMAGE_SUFFIXES
    ]
    return sorted(files, key=lambda path: path.name)
