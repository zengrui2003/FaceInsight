import pytest

import face_insight.config as config_module
import face_insight.storage as storage_module
from face_insight.config import (
    BaiduConfig,
    ConfigError,
    load_baidu_config,
    prepare_first_run,
    save_baidu_config,
)
from face_insight.face_analysis import FaceAnalyzer, aggregate_scores, verify_baidu_config
from face_insight.storage import calculate_average, connect


def test_aggregate_scores():
    counts = aggregate_scores([0, 1, 3, 3, 10])
    assert counts == [1, 1, 0, 2, 0, 0, 0, 0, 0, 0, 1]


def test_average_only_counts_faces():
    counts = [0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 1]
    assert calculate_average(counts) == 4.25


def test_average_with_no_face_does_not_divide_by_zero():
    assert calculate_average([3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) is None


def test_detect_score_retries_sdk108(monkeypatch):
    analyzer = FaceAnalyzer.__new__(FaceAnalyzer)
    analyzer.request_interval = 0
    responses = iter(
        [
            {"error_code": "SDK108", "error_msg": "connection or read data timeout"},
            {"error_code": 0, "result": {"face_list": [{"beauty": 78}]}},
        ]
    )
    monkeypatch.setattr(analyzer, "detect", lambda path: next(responses))
    assert analyzer.detect_score(None) == 8


def test_save_baidu_config_round_trip(tmp_path, monkeypatch):
    target = tmp_path / "config.local.json"
    monkeypatch.setattr(config_module, "get_local_config_path", lambda: target)

    saved = save_baidu_config(BaiduConfig("123", "api-key", "secret-key"), target)
    loaded = load_baidu_config()

    assert saved == target.resolve()
    assert loaded == BaiduConfig("123", "api-key", "secret-key")


def test_load_baidu_config_is_empty_without_saved_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "missing" / "config.local.json"
    monkeypatch.setattr(config_module, "get_local_config_path", lambda: target)

    with pytest.raises(ConfigError, match="三码"):
        load_baidu_config()


def test_legacy_config_is_migrated_and_loaded(tmp_path, monkeypatch):
    target = tmp_path / "config.local.json"
    target.write_text(
        '{"app_id": "old", "api_key": "old", "secret_key": "old"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(config_module, "get_local_config_path", lambda: target)
    monkeypatch.chdir(tmp_path)

    loaded = load_baidu_config()
    migrated = target.read_text(encoding="utf-8")

    assert loaded == BaiduConfig("old", "old", "old")
    assert '"schema_version": 2' in migrated


def test_first_run_clears_legacy_config_only_once(tmp_path, monkeypatch):
    target = tmp_path / "config.local.json"
    target.write_text(
        '{"schema_version": 2, "app_id": "old", "api_key": "old", "secret_key": "old"}',
        encoding="utf-8",
    )
    data_dir = tmp_path / "user-data"
    monkeypatch.setenv("FACEINSIGHT_DATA_DIR", str(data_dir))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(config_module, "get_local_config_path", lambda: target)

    assert prepare_first_run() is True
    assert not target.exists()
    assert (data_dir / ".first_run_complete").exists()

    save_baidu_config(BaiduConfig("new", "new", "new"), target)
    assert prepare_first_run() is False
    assert load_baidu_config() == BaiduConfig("new", "new", "new")


def test_verify_baidu_config_reports_auth_error(monkeypatch):
    class FakeClient:
        def __init__(self, app_id, api_key, secret_key):
            pass

        def _auth(self):
            return {"error_code": 14, "error_msg": "IAM Certification failed"}

    monkeypatch.setattr("face_insight.face_analysis.AipFace", FakeClient)

    with pytest.raises(RuntimeError, match="三码验证失败"):
        verify_baidu_config(BaiduConfig("123", "api-key", "secret-key"))


def test_default_db_path_uses_current_user_local_data(tmp_path, monkeypatch):
    monkeypatch.delenv("FACEINSIGHT_DATA_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert storage_module.get_default_db_path() == tmp_path / "FaceBeautyAnalysisSystem" / "beauty_analysis.db"


def test_legacy_shared_database_is_removed(tmp_path, monkeypatch):
    legacy = tmp_path / "beauty_analysis.db"
    legacy.write_bytes(b"legacy")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(storage_module, "DEFAULT_DB_PATH", tmp_path / "new" / "beauty_analysis.db")

    removed = storage_module.remove_legacy_databases()

    assert removed == [legacy.resolve()]
    assert not legacy.exists()


def test_connect_creates_database_directory(tmp_path):
    database = tmp_path / "nested" / "beauty_analysis.db"

    with connect(database) as conn:
        conn.execute("SELECT 1")

    assert database.parent.exists()
