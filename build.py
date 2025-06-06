#!/usr/bin/env python3
import pathlib
import logging
import os
import sys
import json
from typing import Optional
import subprocess
from tap import Tap
from pydantic import BaseModel, Field

IMAGE_OWNER = "vxdxk"

if os.getenv("GITHUB_ACTIONS") == "true":
    IMAGE_OWNER = f"ghcr.io/{IMAGE_OWNER}"

EXCLUDED_DIRS = set([
    ".git",
    ".github",
    "docs",
])
REPO_DIR = pathlib.Path(__file__).parent.resolve()

class ArgumentParser(Tap):
    image: Optional[str] = None # Name of image to build, or "all" for building all images
    show: bool = False

def execute_command(command: list[str]):
    logging.info(f"Executing command={command}")
    subprocess.run(command, check=True) 

class ExitHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        if record.levelno in (logging.ERROR, logging.CRITICAL):
            sys.exit(1)

class ImageConfig(BaseModel):
    tag: str = "latest"
    dependencies: list[str] = Field(default_factory=list)
    deploy: bool = True

    def __str__(self) -> str:
        return '%s' % (
            ' '.join('%s=%s' % item for item in vars(self).items())
        )

TargetsDict = dict[str, tuple[pathlib.Path, ImageConfig]]
def show_targets(targets: TargetsDict):
    print("TARGETS:")
    for name, (_, config) in targets.items():
        print(f" {name:20}| {config} |")

def load_meta_file() -> Optional[ImageConfig]:
    current_dir = pathlib.Path.cwd()
    meta_path = current_dir / "meta.json"
    
    if not meta_path.exists():
        logging.warning("Meta file not found in directory: %s", current_dir)
        return None
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            return ImageConfig.model_validate_json(f.read())
    except json.JSONDecodeError as e:
        logging.error("Failed to parse JSON: %s", str(e))
        return None
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))
        return None

def image_build(name: str, config: ImageConfig):
    logging.info(f"Building {name} with config: {config}")
    try:
        execute_command(["docker", "buildx", "build", "-t", f"{IMAGE_OWNER}/{name}:{config.tag}", "."])
    except Exception as e:
        logging.error(f"Failed to build image with error={e}")

def main():
    args = ArgumentParser().parse_args()
    targets: TargetsDict = {}
    for entry in REPO_DIR.iterdir():
        if entry.is_dir() and entry.name not in EXCLUDED_DIRS:
            name = entry.name
            logging.info(f"Directory: {entry.name}")
            os.chdir(entry)
            meta_info = load_meta_file()
            if meta_info is None:
                logging.warning(f"Meta for {name} is None")
                continue
            targets[name] = (entry, meta_info)
    if args.show:
        print("Showing targets")
        show_targets(targets)
    
    if args.image is not None:
        if args.image.lower() == "all":
            for target, (dir, config) in targets.items():
                os.chdir(dir)
                image_build(target, config)
        elif targets.get(args.image) is not None:
            (dir, conf) = targets[args.image]
            os.chdir(dir)
            image_build(args.image, conf)
        else:
            logging.error(f"No such image={args.image}, available images={targets.keys()}")

if __name__ == "__main__":
    log_level = logging.DEBUG if os.getenv("DEV") is not None else logging.WARN
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(funcName)s() -> %(message)s',
        handlers=[ExitHandler()]
    )
    main()
