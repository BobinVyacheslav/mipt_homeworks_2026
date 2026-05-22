from pathlib import Path
import sys

PROJECT_PARENT = Path(__file__).resolve().parent.parent
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))


def main() -> None:
    from final_project.ai_chat.main import main as package_main

    package_main()


if __name__ == '__main__':
    main()
