import os
import importlib


def load_modules():
    """
    Carga dinámica de módulos de seguridad.

    Retorna:
    {
        "module_name": {
            "detector": function,
            "response": function
        }
    }
    """

    modules = {}

    base_path = "modules"

    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)

        if not os.path.isdir(category_path):
            continue

        for attack in os.listdir(category_path):
            attack_path = os.path.join(category_path, attack)

            if not os.path.isdir(attack_path):
                continue

            module_name = f"{category}.{attack}"

            try:
                detector_module = importlib.import_module(
                    f"modules.{category}.{attack}.detector"
                )

                response_module = importlib.import_module(
                    f"modules.{category}.{attack}.response"
                )

                modules[module_name] = {
                    "detector": getattr(detector_module, "detect", None),
                    "response": getattr(response_module, "respond", None),
                }

            except Exception as e:
                print(f"[LOAD ERROR] {module_name}: {e}")

    return modules