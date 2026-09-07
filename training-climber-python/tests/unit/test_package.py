import json
from pathlib import Path

from climber_training.rule_engine import exportar_ruleset, validate_rule_package

ROOT = Path(__file__).resolve().parents[2]


def test_packages_are_valid():
    assert validate_rule_package(ROOT / "rules" / "demo") == []
    assert validate_rule_package(ROOT / "rules" / "1.0.0-candidate") == []


def test_unknown_parameter_fails_atomically(tmp_path):
    source = ROOT / "rules" / "demo"
    package = tmp_path / "invalid"; package.mkdir()
    for item in source.glob("*.json"):
        package.joinpath(item.name).write_bytes(item.read_bytes())
    rules = json.loads((package / "rules.json").read_text(encoding="utf-8"))
    rules[0]["actions"][1]["parameter_id"] = "MISSING"
    (package / "rules.json").write_text(json.dumps(rules), encoding="utf-8")
    assert any("unknown ParameterID" in e for e in validate_rule_package(package))


def test_unknown_source_fails(tmp_path):
    source = ROOT / "rules" / "demo"
    package = tmp_path / "invalid"; package.mkdir()
    for item in source.glob("*.json"):
        package.joinpath(item.name).write_bytes(item.read_bytes())
    mappings = json.loads((package / "rule_evidence.json").read_text(encoding="utf-8"))
    mappings[0]["source_id"] = "MISSING"
    (package / "rule_evidence.json").write_text(json.dumps(mappings), encoding="utf-8")
    assert any("Broken SourceID" in e for e in validate_rule_package(package))


def test_export_is_reproducible(tmp_path):
    first, second = tmp_path / "one.zip", tmp_path / "two.zip"
    exportar_ruleset(ROOT / "rules" / "demo", first)
    exportar_ruleset(ROOT / "rules" / "demo", second)
    assert first.read_bytes() == second.read_bytes()
