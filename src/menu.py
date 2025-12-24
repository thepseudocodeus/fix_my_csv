from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import logging

from .git_tools.git import GitModule
from .csv_tools.profiler import CSVProfilerModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Menu")


def main():
    modules = [GitModule(), CSVProfilerModule()]

    while True:
        module = inquirer.select(
            message="Select Module:",
            choices=[Choice(m, m.name) for m in modules] + [Choice(None, "Exit")],
        ).execute()

        if not module:
            logger.info("Goodbye!")
            break

        while True:
            action = inquirer.select(
                message=f"{module.name} - Select Action:",
                choices=[Choice(item, item.label) for item in module.items()]
                + [Choice(None, "← Back")],
            ).execute()

            if not action:
                break

            try:
                action.handler()
            except Exception as e:
                logger.exception(f"Error: {e}")
                input("Press Enter to continue...")


if __name__ == "__main__":
    main()
