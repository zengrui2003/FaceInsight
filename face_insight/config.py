from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    """百度智能云三码没有配置完整。"""


@dataclass(frozen=True)
class BaiduConfig:
    app_id: str
    api_key: str
    secret_key: str


def load_baidu_config() -> BaiduConfig:
    """优先读取环境变量，也支持本地 config.local.json。"""
    values = {
        "app_id": os.getenv("BAIDU_APP_ID", ""),
        "api_key": os.getenv("BAIDU_API_KEY", ""),
        "secret_key": os.getenv("BAIDU_SECRET_KEY", ""),
    }

    search_paths = [Path("config.local.json")]
    if getattr(sys, "frozen", False):
        search_paths.append(Path(sys.executable).parent / "config.local.json")
    search_paths.append(Path(__file__).parent.parent / "config.local.json")

    config_file = next((path for path in search_paths if path.exists()), None)
    if config_file:
        local = json.loads(config_file.read_text(encoding="utf-8"))
        for key in values:
            values[key] = str(local.get(key) or values[key]).strip()

    missing = [key.upper() for key, value in values.items() if not value]
    if missing:
        raise ConfigError(
            "缺少百度智能云三码："
            + "、".join(missing)
            + "。请设置环境变量，或复制 config.local.json.example 后填写真实值。"
        )
    return BaiduConfig(**values)
