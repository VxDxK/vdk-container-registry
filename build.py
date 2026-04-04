#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pydantic>=2.0",
#   "rich>=13.7.0",
#   "typer>=0.12.0",
# ]
# ///

import pathlib
import logging
import os
import sys
from typing import Optional, Annotated
import subprocess
from collections import defaultdict, deque

import typer
from pydantic import BaseModel, Field
from pathlib import Path
from rich.console import Console
from rich.table import Table

IMAGE_OWNER: str = "vxdxk"
if os.getenv("GITHUB_ACTIONS") == "true":
    IMAGE_OWNER = f"ghcr.io/{IMAGE_OWNER}"

REPO_DIR: Path = pathlib.Path(__file__).parent.resolve()
DIST_DIR: Path = REPO_DIR / "dist"
EXCLUDED_DIRS: set[str] = {
    DIST_DIR.name,
    ".git",
    ".github",
    "docs",
    "venv",
    ".venv",
    ".idea",
    "__pycache__",
    "*egg-info", # TODO: Add regex support for excludes
}

SHARED_DIRS: set[Path] = set()


class ImageConfig(BaseModel):
    tag: str = "latest"
    dependencies: list[str] = Field(default_factory=list)

    def __str__(self) -> str:
        return " ".join(f"{k}={v}" for k, v in self.model_dump().items())


TargetsDict = dict[str, tuple[Path, ImageConfig]]


def load_meta_file(meta_path: Path) -> Optional[ImageConfig]:
    if not meta_path.exists():
        logging.warning("Meta file not found: %s", meta_path)
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return ImageConfig.model_validate_json(f.read())
    except Exception as e:
        logging.error("Failed to load %s: %s", meta_path, e)
        return None


def get_shared_context_flags() -> list[str]:
    flags: list[str] = []
    for shared_path in SHARED_DIRS:
        if not shared_path.exists():
            logging.warning("Shared directory not found (skipped): %s", shared_path)
            continue
        name: str = shared_path.name
        flags.extend(["--build-context", f"{name}={shared_path.resolve()}"])
    return flags


def image_build(name: str, config: ImageConfig, context: Path) -> None:
    full_tag: str = f"{IMAGE_OWNER}/{name}:{config.tag}"
    logging.info("Building %s → %s", name, full_tag)

    cmd: list[str] = [
        "docker",
        "buildx",
        "build",
        "-t",
        full_tag,
        ".",
    ]
    cmd.extend(get_shared_context_flags())

    logging.info("Executing: %s (cwd=%s)", " ".join(cmd), context)
    try:
        subprocess.run(cmd, check=True, cwd=context)
    except Exception as e:
        logging.error("Failed to build %s: %s", name, e)
        raise


def image_exists(full_tag: str) -> bool:
    try:
        subprocess.run(
            ["docker", "image", "inspect", full_tag],
            check=True,
            capture_output=True,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def export_image(name: str, tag: str) -> None:
    full_tag: str = f"{IMAGE_OWNER}/{name}:{tag}"
    output_path: Path = DIST_DIR / f"{name}-{tag}.tar.gz"
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Exporting %s → %s", full_tag, output_path)

    if not image_exists(full_tag):
        raise ValueError(f"Image {full_tag} does not exist locally. Build it first!")

    try:
        subprocess.run(
            f"docker save {full_tag} | gzip > {output_path}",
            shell=True,
            check=True,
            cwd=REPO_DIR,
        )
        logging.info("Successfully exported to %s", output_path)
    except Exception as e:
        logging.error("Failed to export %s: %s", name, e)
        raise


def get_full_build_order(targets: TargetsDict) -> list[str]:
    if not targets:
        return []

    graph: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = {name: 0 for name in targets}

    for name, (_, config) in targets.items():
        for dep in config.dependencies:
            if dep not in targets:
                raise ValueError(f"Image '{name}' depends on missing image '{dep}'")
            graph[dep].append(name)
            indegree[name] += 1

    queue: deque[str] = deque([name for name, deg in indegree.items() if deg == 0])
    order: list[str] = []

    while queue:
        current: str = queue.popleft()
        order.append(current)
        for dependent in graph[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(targets):
        raise ValueError("Cyclic dependencies detected!")
    return order


def get_transitive_dependencies(selected: str, targets: TargetsDict) -> set[str]:
    if selected not in targets:
        raise ValueError(f"Image '{selected}' not found")

    needed: set[str] = set()
    stack: list[str] = [selected]
    while stack:
        name: str = stack.pop()
        if name in needed:
            continue
        needed.add(name)
        for dep in targets[name][1].dependencies:
            if dep not in targets:
                raise ValueError(f"Missing dependency '{dep}' for '{name}'")
            stack.append(dep)
    return needed


def get_build_order(
    selected: str, targets: TargetsDict, full_order: list[str]
) -> list[str]:
    if selected.lower() == "all":
        return full_order
    needed: set[str] = get_transitive_dependencies(selected, targets)
    return [name for name in full_order if name in needed]


app = typer.Typer(
    name="build",
    help="Docker build tool for vxdxk repository (with dependencies, export and shared contexts)",
    add_completion=True,
)


def _load_all_targets() -> TargetsDict:
    targets: TargetsDict = {}
    for entry in REPO_DIR.iterdir():
        if entry.is_dir() and entry.name not in EXCLUDED_DIRS and not entry.name.startswith("."):
            meta_path: Path = entry / "meta.json"
            meta_info: Optional[ImageConfig] = load_meta_file(meta_path)
            if meta_info:
                targets[entry.name] = (entry, meta_info)
            else:
                logging.warning("Skipping %s (no valid meta.json)", entry.name)
    return targets


@app.command()
def show() -> None:
    targets: TargetsDict = _load_all_targets()
    if not targets:
        print("No images found")
        return

    console = Console()

    try:
        get_full_build_order(targets)
        console.print("[green]✓ No cyclic dependencies[/green]")
    except ValueError as e:
        console.print(f"[red]✗ ERROR: {e}[/red]")
        return

    table = Table(title="Docker Images", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Tag", style="green")
    table.add_column("Dependencies", style="yellow")

    for name, (_, config) in sorted(targets.items()):
        deps: str = ", ".join(config.dependencies) if config.dependencies else "—"
        table.add_row(name, config.tag, deps)

    console.print(table)


@app.command()
def build(
    image: Annotated[str, typer.Argument(help="Image name or 'all'")] = "all",
    export: Annotated[
        bool, typer.Option("--export", help="Export built images to dist/*.tar.gz")
    ] = False,
) -> None:
    targets: TargetsDict = _load_all_targets()
    if not targets:
        logging.warning("No images to build")
        return

    try:
        full_order: list[str] = get_full_build_order(targets)
        order_to_build: list[str] = get_build_order(image, targets, full_order)

        logging.info("Build order: %s", order_to_build)

        for name in order_to_build:
            context_dir: Path
            config: ImageConfig
            context_dir, config = targets[name]
            image_build(name, config, context_dir)

            if export:
                export_image(name, config.tag)

    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)


@app.command()
def export(
    image: Annotated[str, typer.Argument(help="Image name to export")],
    tag: Annotated[
        Optional[str],
        typer.Option("--tag", "-t", help="Tag to export (default: from meta.json)"),
    ] = None,
) -> None:
    targets: TargetsDict = _load_all_targets()
    if image not in targets:
        logging.error("Image '%s' not found", image)
        sys.exit(1)

    config: ImageConfig = targets[image][1]
    final_tag: str = tag if tag is not None else config.tag

    try:
        export_image(image, final_tag)
    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)


# Need for
def main():
    app()


if __name__ == "__main__":
    log_level: int = logging.DEBUG if os.getenv("DEV") else logging.WARN
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(funcName)s() → %(message)s",
    )

    class ExitHandler(logging.StreamHandler):
        def emit(self, record: logging.LogRecord) -> None:
            super().emit(record)
            if record.levelno in (logging.ERROR, logging.CRITICAL):
                sys.exit(1)

    logging.getLogger().handlers = [ExitHandler()]
    main()
