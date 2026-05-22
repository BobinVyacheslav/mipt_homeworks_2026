from pathlib import Path
import sys

PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))


def main() -> None:
    from final_project.ai_chat.app import create_app
    from final_project.ai_chat.config.validators import ConfigError
    from final_project.ai_chat.console.output import print_error

    try:
        app = create_app()
    except ConfigError as exc:
        print_error(str(exc))
        return
    app.run()


if __name__ == '__main__':
    main()
