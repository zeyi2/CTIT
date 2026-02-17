import os
import subprocess
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any


class BaseTester:
    name: str
    root_dir: Path
    log_dir: Path
    log_file: Path
    llvm_build_dir: Path
    clang_tidy_bin: Path
    run_tidy_script: Path
    logger: logging.Logger

    def __init__(self, name: str, root_dir: Path) -> None:
        self.name = name
        self.root_dir = root_dir
        self.log_dir = root_dir / "logs"
        self.log_file = self.log_dir / f"{name.lower()}.log"
        self.llvm_build_dir = root_dir / "llvm-project" / "build"
        self.clang_tidy_bin = self.llvm_build_dir / "bin" / "clang-tidy"
        self.run_tidy_script = (
            root_dir
            / "llvm-project"
            / "clang-tools-extra"
            / "clang-tidy"
            / "tool"
            / "run-clang-tidy.py"
        )

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        logging.basicConfig(level=logging.INFO, format=f"[{self.name}] %(message)s")
        self.logger = logging.getLogger(self.name)

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> subprocess.CompletedProcess[str]:
        self.logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd or self.root_dir,
            env={**os.environ, **(env or {})},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            self.logger.warning(f"Command failed with exit code {result.returncode}")
        return result

    def cleanup_old_configs(self, search_dir: Path) -> None:
        self.logger.info(f"Cleaning up .clang-tidy files in {search_dir}")
        for path in search_dir.rglob(".clang-tidy"):
            try:
                path.unlink()
                self.logger.debug(f"Removed {path}")
            except OSError as e:
                self.logger.error(f"Failed to remove {path}: {e}")

    def check_dependencies(self) -> None:
        if not self.clang_tidy_bin.exists():
            raise FileNotFoundError(f"clang-tidy not found at {self.clang_tidy_bin}")
        if not self.run_tidy_script.exists():
            raise FileNotFoundError(
                f"run-clang-tidy.py not found at {self.run_tidy_script}"
            )

    def run_tidy(
        self,
        check_name: str,
        build_dir: Path,
        target_dir: Optional[Path] = None,
        extra_config: Optional[str] = None,
    ) -> subprocess.CompletedProcess[str]:
        self.logger.info(f"Running clang-tidy for check: {check_name}")

        tidy_args: List[str] = [
            "python3",
            str(self.run_tidy_script),
            "-clang-tidy-binary",
            str(self.clang_tidy_bin),
            "-p",
            str(build_dir),
            f"-checks=-*,{check_name}",
            "-quiet",
        ]

        if extra_config:
            tidy_args.append(f"-config={extra_config}")

        if target_dir:
            # ^$TARGET_DIR/.*(?<!\.S)$
            escaped_path = re.escape(str(target_dir))
            regex = f"^{escaped_path}/.*(?<!\\.S)$"
            tidy_args.append(regex)

        result = self.run_command(tidy_args)

        with open(self.log_file, "w") as f:
            f.write(result.stdout)

        self.logger.info(f"Finished. Log saved to {self.log_file}")
        return result

    def prepare(self) -> None:
        """To be implemented by subclasses"""
        pass

    def execute(self, check_name: str, extra_config: Optional[str] = None) -> None:
        """Main entry point for the tester"""
        self.check_dependencies()
        self.prepare()
        pass
