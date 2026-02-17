import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Type
from testers.projects.cppcheck import CppcheckTester
from testers.projects.llvm import LLVMTester
from testers.base import BaseTester

def main() -> None:
    parser = argparse.ArgumentParser(description="Run Clang-Tidy integration tests.")
    parser.add_argument("project", choices=["cppcheck", "llvm"], help="Project to test")
    parser.add_argument("check_name", help="Name of the clang-tidy check to run")
    parser.add_argument("--config", help="Extra clang-tidy configuration", default=os.environ.get("TIDY_CONFIG"))

    args = parser.parse_args()
    root_dir = Path(os.getcwd())

    # Map project names to their respective tester classes
    project_map: Dict[str, Type[BaseTester]] = {
        "cppcheck": CppcheckTester,
        "llvm": LLVMTester
    }

    tester_class = project_map.get(args.project)
    if not tester_class:
        # This case is actually handled by argparse choices, but good for safety
        print(f"Error: Unknown project '{args.project}'")
        sys.exit(1)

    try:
        tester = tester_class(root_dir)
        tester.execute(args.check_name, extra_config=args.config)
    except Exception as e:
        print(f"Error running tester for {args.project}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
