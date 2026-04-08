#!/usr/bin/env python3
"""Validate frontmatter for Copilot customization files.

This script is designed to be reused by:
- pre-commit (file-targeted validation)
- Copilot hooks (workspace-level blocking validation)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except Exception as exc:  # pragma: no cover
    print(f"ERROR: missing dependency for YAML parsing: {exc}", file=sys.stderr)
    sys.exit(2)


ROOT = Path(__file__).resolve().parents[1]
CUSTOMIZATION_PATTERNS = (
    "tools/copilot/agents/*.agent.md",
    "tools/copilot/orchestrators/*.agent.md",
    "tools/copilot/prompts/*.prompt.md",
    ".github/instructions/*.instructions.md",
)


@dataclass
class ValidationError:
    path: Path
    message: str


def _is_customization_file(path: Path) -> bool:
    normalized = path.as_posix()
    return (
        (normalized.startswith("tools/copilot/agents/") and normalized.endswith(".agent.md"))
        or (normalized.startswith("tools/copilot/orchestrators/") and normalized.endswith(".agent.md"))
        or (normalized.startswith("tools/copilot/prompts/") and normalized.endswith(".prompt.md"))
        or (normalized.startswith(".github/instructions/") and normalized.endswith(".instructions.md"))
    )


def _collect_targets(raw_paths: list[str]) -> list[Path]:
    if raw_paths:
        paths = [Path(p) for p in raw_paths]
        rel_paths: list[Path] = []
        for candidate in paths:
            resolved = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
            try:
                rel = resolved.relative_to(ROOT)
            except ValueError:
                continue
            if _is_customization_file(rel):
                rel_paths.append(rel)
        return sorted(set(rel_paths))

    discovered: set[Path] = set()
    for pattern in CUSTOMIZATION_PATTERNS:
        for file_path in ROOT.glob(pattern):
            if file_path.is_file():
                discovered.add(file_path.relative_to(ROOT))
    return sorted(discovered)


def _extract_frontmatter(path: Path) -> tuple[dict[str, object] | None, list[ValidationError]]:
    errors: list[ValidationError] = []
    absolute_path = ROOT / path
    text = absolute_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        errors.append(ValidationError(path, "frontmatter must start at first line with '---'"))
        return None, errors

    closing_index = -1
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index == -1:
        errors.append(ValidationError(path, "frontmatter is not closed with a second '---'"))
        return None, errors

    yaml_text = "\n".join(lines[1:closing_index])
    try:
        data = yaml.safe_load(yaml_text) if yaml_text.strip() else None
    except yaml.YAMLError as exc:
        errors.append(ValidationError(path, f"invalid YAML frontmatter: {exc}"))
        return None, errors

    if not isinstance(data, dict):
        errors.append(ValidationError(path, "frontmatter must be a YAML mapping/object"))
        return None, errors

    return data, errors


def _validate_common(path: Path, frontmatter: dict[str, object]) -> list[ValidationError]:
    errors: list[ValidationError] = []

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(ValidationError(path, "missing required non-empty string field: name"))

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(ValidationError(path, "missing required non-empty string field: description"))
    elif not description.strip().lower().startswith("use when"):
        errors.append(ValidationError(path, "description should start with 'Use when' for discoverability"))

    tools = frontmatter.get("tools")
    if tools is not None:
        if not isinstance(tools, list) or not all(isinstance(item, str) and item.strip() for item in tools):
            errors.append(ValidationError(path, "tools must be a list of non-empty strings"))

    argument_hint = frontmatter.get("argument-hint")
    if argument_hint is not None and (not isinstance(argument_hint, str) or not argument_hint.strip()):
        errors.append(ValidationError(path, "argument-hint must be a non-empty string when present"))

    user_invocable = frontmatter.get("user-invocable")
    if user_invocable is not None and not isinstance(user_invocable, bool):
        errors.append(ValidationError(path, "user-invocable must be a boolean when present"))

    agents = frontmatter.get("agents")
    if agents is not None:
        if not isinstance(agents, list) or not all(isinstance(item, str) and item.strip() for item in agents):
            errors.append(ValidationError(path, "agents must be a list of non-empty strings when present"))

    return errors


def _validate_agent_specific(
    path: Path, frontmatter: dict[str, object], known_agent_names: set[str]
) -> list[ValidationError]:
    errors: list[ValidationError] = []

    if not path.name.endswith(".agent.md"):
        return errors

    agents = frontmatter.get("agents")
    if isinstance(agents, list):
        for referenced_agent in agents:
            if isinstance(referenced_agent, str) and referenced_agent not in known_agent_names:
                errors.append(
                    ValidationError(
                        path,
                        f"agents references unknown agent name: '{referenced_agent}'",
                    )
                )

    tools = frontmatter.get("tools")
    tool_set = {item for item in tools if isinstance(item, str)} if isinstance(tools, list) else set()
    name = frontmatter.get("name")

    if path.name.startswith("orchestrator-") and "agent" not in tool_set:
        errors.append(ValidationError(path, "orchestrator-* agent files must include the 'agent' tool"))

    if isinstance(name, str) and name.startswith("Orchestrator |") and not path.name.startswith("orchestrator-"):
        errors.append(
            ValidationError(path, "agent name starting with 'Orchestrator |' must use file prefix orchestrator-")
        )

    return errors


def _validate_prompt_specific(path: Path, frontmatter: dict[str, object]) -> list[ValidationError]:
    errors: list[ValidationError] = []

    if not path.name.endswith(".prompt.md"):
        return errors

    name = frontmatter.get("name")

    if path.name.startswith("lifecore-") and isinstance(name, str) and not name.startswith("lifecore |"):
        errors.append(ValidationError(path, "lifecore-* prompt files must have a name starting with 'lifecore |'"))

    if isinstance(name, str) and name.startswith("lifecore |") and not path.name.startswith("lifecore-"):
        errors.append(ValidationError(path, "prompt name starting with 'lifecore |' must use file prefix lifecore-"))

    return errors


def _collect_agent_names(frontmatters: dict[Path, dict[str, object]]) -> tuple[set[str], list[ValidationError]]:
    errors: list[ValidationError] = []
    names: set[str] = set()
    seen: dict[str, Path] = {}

    for path, data in frontmatters.items():
        if not path.name.endswith(".agent.md"):
            continue
        candidate = data.get("name")
        if not isinstance(candidate, str) or not candidate.strip():
            continue
        if candidate in seen:
            errors.append(
                ValidationError(
                    path,
                    f"duplicate agent name '{candidate}' already declared in {seen[candidate].as_posix()}",
                )
            )
            continue
        names.add(candidate)
        seen[candidate] = path

    return names, errors


def _render_errors(errors: Iterable[ValidationError]) -> str:
    return "\n".join(f"- {err.path.as_posix()}: {err.message}" for err in errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Copilot customization frontmatter.")
    parser.add_argument("paths", nargs="*", help="Optional paths (pre-commit passes staged files).")
    parser.add_argument(
        "--hook-json",
        action="store_true",
        help="Emit Copilot hook JSON output and block the session on validation errors.",
    )
    args = parser.parse_args()

    targets = _collect_targets(args.paths)
    if not targets:
        if args.hook_json:
            print(json.dumps({"continue": True}))
        return 0

    errors: list[ValidationError] = []
    frontmatters: dict[Path, dict[str, object]] = {}

    for path in targets:
        data, parse_errors = _extract_frontmatter(path)
        errors.extend(parse_errors)
        if data is None:
            continue
        frontmatters[path] = data
        errors.extend(_validate_common(path, data))

    known_agent_names, agent_name_errors = _collect_agent_names(frontmatters)
    errors.extend(agent_name_errors)

    for path, data in frontmatters.items():
        errors.extend(_validate_agent_specific(path, data, known_agent_names))
        errors.extend(_validate_prompt_specific(path, data))

    if not errors:
        if args.hook_json:
            print(json.dumps({"continue": True}))
        return 0

    rendered = _render_errors(errors)

    if args.hook_json:
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": "Customization frontmatter validation failed",
                    "systemMessage": (f"Fix customization metadata before continuing:\n{rendered}"),
                }
            )
        )
        return 2

    print("Customization frontmatter validation failed:", file=sys.stderr)
    print(rendered, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
