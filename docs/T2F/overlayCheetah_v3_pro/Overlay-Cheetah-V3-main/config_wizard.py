#!/usr/bin/env python3
"""
Interactive configuration wizard for autocoder tasks
"""

import sys
from pathlib import Path
from typing import Dict, Any
import yaml


def print_banner():
    """Print wizard banner"""
    print("\n" + "=" * 60)
    print(" Overlay Cheetah Autocoder - Configuration Wizard")
    print("=" * 60 + "\n")


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with default value"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    value = input(prompt).strip()
    return value if value else default


def select_template_type() -> str:
    """Select template type"""
    print("\nAvailable template types:")
    print("  1. Python Module")
    print("  2. Python API (FastAPI)")
    print("  3. JavaScript/TypeScript Component")
    print("  4. Generic/Custom")

    choice = get_input("\nSelect template type (1-4)", "1")

    templates = {
        "1": "python/generic.py.j2",
        "2": "python/api.py.j2",
        "3": "javascript/component.js.j2",
        "4": "custom",
    }

    return templates.get(choice, "python/generic.py.j2")


def configure_python_module() -> Dict[str, Any]:
    """Configure Python module context"""
    context = {
        "description": get_input("Module description", "Python module"),
    }

    # Imports
    add_imports = get_input("Add imports? (y/n)", "n").lower() == "y"
    if add_imports:
        imports = []
        print("\nEnter imports (one per line, empty line to finish):")
        while True:
            imp = get_input("Import")
            if not imp:
                break
            imports.append(imp)
        if imports:
            context["imports"] = imports

    # Classes
    add_classes = get_input("\nAdd classes? (y/n)", "n").lower() == "y"
    if add_classes:
        classes = []
        while True:
            print("\n--- Class Configuration ---")
            class_name = get_input("Class name (empty to finish)")
            if not class_name:
                break

            class_info = {
                "name": class_name,
                "docstring": get_input("Class docstring", f"{class_name} class"),
            }

            # Methods
            add_methods = get_input("Add methods? (y/n)", "n").lower() == "y"
            if add_methods:
                methods = []
                while True:
                    method_name = get_input("Method name (empty to finish)")
                    if not method_name:
                        break

                    method = {
                        "name": method_name,
                        "docstring": get_input(
                            "Method docstring", f"{method_name} method"
                        ),
                    }
                    methods.append(method)

                if methods:
                    class_info["methods"] = methods

            classes.append(class_info)

        if classes:
            context["classes"] = classes

    return context


def configure_api() -> Dict[str, Any]:
    """Configure FastAPI context"""
    context = {
        "description": get_input("API description", "REST API"),
        "app_name": get_input("Application name", "API"),
    }

    # Models
    add_models = get_input("Add data models? (y/n)", "y").lower() == "y"
    if add_models:
        models = []
        print("\n--- Data Models ---")
        while True:
            model_name = get_input("Model name (empty to finish)")
            if not model_name:
                break

            model = {"name": model_name, "fields": []}

            print(f"\nFields for {model_name}:")
            while True:
                field_name = get_input("Field name (empty to finish)")
                if not field_name:
                    break

                field_type = get_input(f"Type for {field_name}", "str")
                field = {"name": field_name, "type": field_type}

                has_default = get_input("Has default value? (y/n)", "n").lower() == "y"
                if has_default:
                    default = get_input("Default value")
                    field["default"] = default

                model["fields"].append(field)

            models.append(model)

        if models:
            context["models"] = models

    # Endpoints
    add_endpoints = get_input("\nAdd API endpoints? (y/n)", "y").lower() == "y"
    if add_endpoints:
        endpoints = []
        print("\n--- API Endpoints ---")
        while True:
            path = get_input("Endpoint path (empty to finish, e.g., /users)")
            if not path:
                break

            endpoint = {
                "path": path,
                "method": get_input("HTTP method", "get").lower(),
                "function_name": get_input(
                    "Function name", path.replace("/", "_").strip("_")
                ),
                "docstring": get_input("Endpoint description", f"{path} endpoint"),
            }

            endpoints.append(endpoint)

        if endpoints:
            context["endpoints"] = endpoints

    return context


def create_task_file(output_path: Path):
    """Create a task file interactively"""
    print_banner()

    # Task ID
    task_id = get_input("Task ID", "my_task")

    # Files to generate
    files = []

    while True:
        print("\n" + "-" * 60)
        print(f"Configuring file #{len(files) + 1}")
        print("-" * 60)

        output_file = get_input(
            "\nOutput file path (empty to finish, e.g., src/api.py)"
        )
        if not output_file:
            break

        template = select_template_type()

        # Get context based on template
        if template == "python/api.py.j2":
            context = configure_api()
        elif template == "python/generic.py.j2":
            context = configure_python_module()
        else:
            print("\nContext configuration (key=value, empty to finish):")
            context = {}
            while True:
                kv = get_input("Key=Value")
                if not kv or "=" not in kv:
                    break
                key, value = kv.split("=", 1)
                context[key.strip()] = value.strip()

        files.append({"template": template, "output": output_file, "context": context})

        another = get_input("\nAdd another file? (y/n)", "n").lower()
        if another != "y":
            break

    if not files:
        print("\nNo files configured. Exiting.")
        return

    # Create task configuration
    task = {"task_id": task_id, "files": files}

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        yaml.dump(task, f, default_flow_style=False, sort_keys=False)

    print(f"\n✓ Task configuration saved to: {output_path}")
    print(f"\nTo generate files, run:")
    print(f"  python autocoder_enhanced.py --once")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        tasks_dir = Path(__file__).parent / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        filename = get_input("\nTask filename", "my_task.yaml")
        if not filename.endswith(".yaml"):
            filename += ".yaml"

        output_path = tasks_dir / filename

    try:
        create_task_file(output_path)
    except KeyboardInterrupt:
        print("\n\nWizard cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
