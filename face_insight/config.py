from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    """百度智能云三码没有配置完整。"""


CONFIG_SCHEMA_VERSION = 2
FIRST_RUN_MARKER_NAME = ".first_run_complete"


@dataclass(frozen=True)
class BaiduConfig:
    app_id: str
    api_key: str
    secret_key: str


def get_local_config_path() -> Path:
    """返回当前运行方式下最适合保存配置的位置。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "config.local.json"
    return Path(__file__).resolve().parent.parent / "config.local.json"


def get_user_data_dir() -> Path:
    override = os.getenv("FACEINSIGHT_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data).resolve() / "FaceBeautyAnalysisSystem"
    return Path.home() / ".faceinsight"


def prepare_first_run() -> bool:
    """每个 Windows 用户第一次使用时清空旧配置，强制重新手动填写。"""
    marker = get_user_data_dir() / FIRST_RUN_MARKER_NAME
    if marker.exists():
        return False

    candidates = [get_local_config_path(), Path.cwd() / "config.local.json"]
    for config_file in dict.fromkeys(path.resolve() for path in candidates):
        if config_file.exists():
            try:
                config_file.unlink()
            except OSError:
                pass

    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("1\n", encoding="utf-8")
    return True


def save_baidu_config(config: BaiduConfig, path: Path | None = None) -> Path:
    """原子写入本地配置，避免程序异常退出时留下半截 JSON。"""
    target = (path or get_local_config_path()).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "app_id": config.app_id.strip(),
        "api_key": config.api_key.strip(),
        "secret_key": config.secret_key.strip(),
    }
    temp_path = target.with_suffix(target.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(target)
    return target


def load_baidu_config() -> BaiduConfig:
    """读取用户在界面中保存的本地配置。"""
    values = {
        "app_id": "",
        "api_key": "",
        "secret_key": "",
    }

    search_paths = [get_local_config_path(), Path("config.local.json")]
    search_paths = list(dict.fromkeys(path.resolve() for path in search_paths))

    config_file = next((path for path in search_paths if path.exists()), None)
    if config_file:
        try:
            local = json.loads(config_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigError(f"配置文件无法读取：{config_file}（{exc}）") from exc
        if not isinstance(local, dict):
            raise ConfigError(f"配置文件格式错误：{config_file}")
        for key in values:
            values[key] = str(local.get(key) or "").strip()

        if local.get("schema_version") != CONFIG_SCHEMA_VERSION and all(values.values()):
            save_baidu_config(BaiduConfig(**values), config_file)

    missing = [key.upper() for key, value in values.items() if not value]
    if missing:
        raise ConfigError(
            "缺少百度智能云三码："
            + "、".join(missing)
            + "。请在界面中打开“三码配置”并保存。"
        )
    return BaiduConfig(**values)
