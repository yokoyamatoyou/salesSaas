from pathlib import Path

import yaml


def test_cloudrun_configuration():
    path = Path("cloudrun/cloudrun.yaml")
    data = yaml.safe_load(path.read_text())
    container = data["spec"]["template"]["spec"]["containers"][0]
    env = {item["name"]: item["value"] for item in container.get("env", [])}
    assert env.get("APP_ENV") == "production"
    assert env.get("PORT") == "8080"
    assert container["ports"][0]["containerPort"] == 8080
