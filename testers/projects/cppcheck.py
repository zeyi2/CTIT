from pathlib import Path
from typing import Optional
from testers.base import BaseTester

class CppcheckTester(BaseTester):
    source_dir: Path
    build_dir: Path

    def __init__(self, root_dir: Path) -> None:
        super().__init__("Cppcheck", root_dir)
        self.source_dir = self.root_dir / "test-projects" / "cppcheck"
        self.build_dir = self.source_dir / "build"

    def prepare(self) -> None:
        self.cleanup_old_configs(self.source_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        self.run_command([
            "cmake",
            "-S", str(self.source_dir),
            "-B", str(self.build_dir),
            "-G", "Ninja",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_TESTS=ON"
        ])

        self.run_command(["cmake", "--build", str(self.build_dir), "-j"])

    def execute(self, check_name: str, extra_config: Optional[str] = None) -> None:
        self.check_dependencies()
        self.prepare()
        self.run_tidy(check_name, self.build_dir, extra_config=extra_config)
