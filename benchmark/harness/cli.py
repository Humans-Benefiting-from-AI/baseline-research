"""Command-line entry point for the HRE harness.

``--dry-run`` is on by default. A dry run uses the mock adapter and makes
no provider call. ``--no-dry-run`` is the live path and is not used by the
tests.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from harness.models import (
    DEFAULT_MAX_TOKENS,
    PROVIDERS,
    ConfigError,
    parse_providers,
    resolve_model_id,
)
from harness.loader import QuestionLoadError
from harness.report import UnsafeOutputError
from harness.runner import RunConfig, execute, guard_historical_file

BENCHMARK_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = BENCHMARK_DIR / "hre_eval_100.jsonl"
DEFAULT_OUTPUT_DIR = BENCHMARK_DIR / "reports"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="harness",
        description=(
            "Run the Halachic Reasoning Eval. Dry-run is the default and "
            "uses a mock adapter for OpenAI, Anthropic, and Google."
        ),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"JSONL question file (default: {DEFAULT_DATASET.name}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for per-model Markdown and JSON reports.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Score only the first N questions after validation (for a smoke run).",
    )
    parser.add_argument(
        "--providers",
        default=",".join(PROVIDERS),
        help="Comma-separated providers: openai, anthropic, google. Default is all three.",
    )
    parser.add_argument(
        "--openai-model",
        default=None,
        help="OpenAI model id. Overrides OPENAI_MODEL. Default is the packaged current id.",
    )
    parser.add_argument(
        "--anthropic-model",
        default=None,
        help="Anthropic model id. Overrides ANTHROPIC_MODEL.",
    )
    parser.add_argument(
        "--google-model",
        default=None,
        help="Gemini model id. Overrides GOOGLE_MODEL.",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use the mock adapter and make no network call (default: on).",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help=(
            "Enable the LLM-as-judge hook after automatic scoring misses. "
            "Off by default. Ignored during dry-run."
        ),
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=(
            "Output token cap passed to a live adapter "
            f"(default: {DEFAULT_MAX_TOKENS}). Claude thinking tokens count against it."
        ),
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Optional sampling temperature. Omitted unless you set it.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds between live calls. Ignored during dry-run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _load_dotenv()
        config = _config_from_args(args)
        guard_historical_file(BENCHMARK_DIR, config.output_dir)
        reports = execute(config)
    except (QuestionLoadError, ConfigError, UnsafeOutputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    mode = "dry-run" if args.dry_run else "live"
    print(f"HRE harness finished ({mode}).")
    for report in reports:
        accuracy = "n/a" if report.accuracy is None else f"{report.accuracy:.1%}"
        print(
            f"  {report.provider} / {report.model}: "
            f"{report.correct}/{report.scored} scored ({accuracy}), "
            f"errors {report.errors}, empty {report.empty}"
        )
    print(f"Reports: {config.output_dir}")
    if args.dry_run:
        print("No provider was contacted.")
    if args.judge and args.dry_run:
        print("LLM-as-judge stays disabled during dry-run.")
    return 0


def _config_from_args(args: argparse.Namespace) -> RunConfig:
    providers = parse_providers(args.providers)
    explicit = {
        "openai": args.openai_model,
        "anthropic": args.anthropic_model,
        "google": args.google_model,
    }
    model_ids = {
        provider: resolve_model_id(provider, explicit[provider]) for provider in providers
    }
    if args.max_tokens < 1:
        raise ConfigError("--max-tokens must be a positive integer.")
    return RunConfig(
        dataset=args.dataset,
        output_dir=args.output_dir,
        providers=providers,
        model_ids=model_ids,
        limit=args.limit,
        dry_run=args.dry_run,
        judge_enabled=bool(args.judge),
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        sleep_seconds=args.sleep,
    )


def _load_dotenv() -> None:
    """Load ``benchmark/.env`` into the process environment, if python-dotenv is installed.

    Adapters still read keys only from environment variables. Dry-run does
    not read those variables.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(BENCHMARK_DIR / ".env", override=False)


if __name__ == "__main__":
    raise SystemExit(main())
