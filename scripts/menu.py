# menu.py
from pathlib import Path
from typing import List, Dict
from interface import MenuModule
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import importlib
import logging

logger = logging.getLogger("MenuSystem")


class MenuSystem:
    def __init__(self):
        self.modules: Dict[str, MenuModule] = {}
        self._discover_modules()

    def _discover_modules(self):
        """Discover and load modules."""
        modules_dir = Path("modules")
        if not modules_dir.exists():
            logger.warning("No modules directory found")
            return

        for module_file in modules_dir.glob("*_module.py"):
            try:
                module_name = module_file.stem
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, MenuModule)
                        and attr is not MenuModule
                    ):
                        instance = attr()
                        if instance.setup():
                            self.modules[module_name] = instance
                            logger.info(f"Loaded module: {instance.module_name}")
                        else:
                            logger.warning(f"Module setup failed: {module_name}")
                        break

            except Exception as e:
                logger.error(f"Failed to load {module_file}: {e}")

    def register_module(self, name: str, module: MenuModule):
        """Manually register a module."""
        if module.setup():
            self.modules[name] = module
            logger.info(f"Registered: {module.module_name}")

    def run(self):
        """Main menu loop."""
        while True:
            module_choices = [
                Choice(value=name, name=f"📦 {mod.module_name}")
                for name, mod in self.modules.items()
            ] + [Choice(value=None, name="🚪 Exit")]

            selected_module = inquirer.select(
                message="Select a module:", choices=module_choices
            ).execute()

            if selected_module is None:
                logger.info("Exiting menu system")
                break

            self._run_module_menu(selected_module)

    def _run_module_menu(self, module_name: str):
        """Display and handle module-specific menu."""
        module = self.modules[module_name]

        while True:
            items = module.get_menu_items()
            choices = [
                Choice(value=item.id, name=f"{item.label}")
                for item in sorted(items, key=lambda x: x.priority)
            ] + [Choice(value=None, name="⬅️  Back")]

            selection = inquirer.select(
                message=f"{module.module_name} - Select action:", choices=choices
            ).execute()

            if selection is None:
                break

            try:
                module.execute(selection)
            except Exception as e:
                logger.exception(f"Error executing {selection}: {e}")
                inquirer.confirm(message="Continue?", default=True).execute()


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    menu = MenuSystem()
    menu.run()


if __name__ == "__main__":
    main()
