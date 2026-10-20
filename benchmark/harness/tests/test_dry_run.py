from __future__ import annotations

import hashlib
import json
from pathlib import Path

from harness.banner import AUDIT_BANNER
from harness.cli import main
from harness.runner import historical_results_path

BENCHMARK_DIR = Path(__file__).resolve().parents[2]
REQUIRED_BANNER = (
    "Questions not yet audited for halachic accuracy by Elie; "
    "results are not authoritative."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cli_dry_run_limit_writes_three_reports_and_leaves_history(tmp_path: Path):
    historical = historical_results_path(BENCHMARK_DIR)
    before = _sha256(historical)
    output_dir = tmp_path / "reports"

    exit_code = main(
        [
            "--limit",
            "10",
            "--output-dir",
            str(output_dir),
            "--openai-model",
            "gpt-custom",
            "--anthropic-model",
            "claude-custom",
            "--google-model",
            "gemini-custom",
            "--judge",
        ]
    )

    assert exit_code == 0
    assert _sha256(historical) == before
    assert not (output_dir / "hre_results.jsonl").exists()
    assert AUDIT_BANNER == REQUIRED_BANNER

    expected = {
        "openai__gpt-custom.json": "openai",
        "anthropic__claude-custom.json": "anthropic",
        "google__gemini-custom.json": "google",
    }
    for filename, provider in expected.items():
        payload = json.loads((output_dir / filename).read_text(encoding="utf-8"))
        markdown = (output_dir / filename.replace(".json", ".md")).read_text(encoding="utf-8")
        assert payload["banner"] == REQUIRED_BANNER
        assert markdown.startswith(REQUIRED_BANNER)
        assert "- Errors: 0" in markdown
        assert "- Empty: 0" in markdown
        assert payload["provider"] == provider
        assert payload["dry_run"] is True
        assert payload["judge_enabled"] is False
        assert payload["questions"] == 10
        assert payload["scored"] == 10
        assert payload["correct"] == 0
        assert payload["errors"] == 0
        assert payload["empty"] == 0
        assert payload["accuracy"] == 0
        assert all(item["status"] == "scored" for item in payload["items"])
        assert all(item["method"] == "none" for item in payload["items"])
        assert "not contacted" in payload["items"][0]["response"]

    index = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))
    assert index["banner"] == REQUIRED_BANNER
    assert len(index["models"]) == 3
    index_md = (output_dir / "index.md").read_text(encoding="utf-8")
    assert index_md.startswith(REQUIRED_BANNER)
    assert "| Errors | Empty |" in index_md


def test_cli_refuses_to_overwrite_historical_results(tmp_path: Path):
    target = tmp_path / "hre_results.jsonl"
    exit_code = main(
        ["--limit", "1", "--output-dir", str(target), "--providers", "openai"]
    )
    assert exit_code == 1
    assert not target.exists()


def test_default_parser_is_dry_run():
    from harness.cli import build_parser

    args = build_parser().parse_args([])
    assert args.dry_run is True
    assert args.limit is None
    assert args.judge is False
    assert args.max_tokens == 1024
