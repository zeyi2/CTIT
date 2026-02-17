from pathlib import Path
from typing import Optional, List
from testers.base import BaseTester

class LLVMTester(BaseTester):
    source_dir: Path
    build_dir: Path

    def __init__(self, root_dir: Path) -> None:
        super().__init__("LLVM", root_dir)
        self.source_dir = self.root_dir / "llvm-project"
        self.build_dir = self.source_dir / "build"

    def prepare(self) -> None:
        if not (self.build_dir / "compile_commands.json").exists():
            raise FileNotFoundError(f"compile_commands.json not found in {self.build_dir}. Run build.sh first.")

        self.cleanup_old_configs(self.source_dir)

        targets: List[str] = [
            "clang",
            "clangAnalysisFlowSensitiveResources",
            "clang-nvlink-wrapper",
            "clang-sycl-linker",
            "clang-installapi",
            "clang-scan-deps",
            "clang-linker-wrapper"
        ]
        self.run_command(["ninja", "-C", str(self.build_dir)] + targets)

    def execute(self, check_name: str, extra_config: Optional[str] = None) -> None:
        self.check_dependencies()
        self.prepare()

        target_dir = self.source_dir / "clang"
        self.run_tidy(check_name, self.build_dir, target_dir=target_dir, extra_config=extra_config)
