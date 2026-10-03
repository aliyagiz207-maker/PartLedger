import json
from src import config_loader
from src.config_loader import load_config

def test_load_config_reads_json(tmp_path, monkeypatch):
    config_data = {"currency": "₺", "company_name": "PartLedger Test"}
    config_file = tmp_path / "config.json"
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    
    monkeypatch.setattr(config_loader, "get_project_root", lambda: tmp_path)
    
    loaded_config = load_config()
    
    assert loaded_config["currency"] == "₺"
    assert loaded_config["company_name"] == "PartLedger Test"