from typing import Dict, List


PERMISSION_ACTIONS = [
    {"key": "view", "label": "Перегляд"},
    {"key": "create", "label": "Створення"},
    {"key": "edit", "label": "Редагування"},
    {"key": "delete", "label": "Видалення"},
    {"key": "print", "label": "Друк"},
    {"key": "export", "label": "Експорт"},
    {"key": "import", "label": "Імпорт"},
    {"key": "manage", "label": "Керування"},
]

PERMISSION_MODULES = [
    {"key": "crm", "label": "CRM"},
    {"key": "inventory", "label": "Склад"},
    {"key": "sales", "label": "Продажі"},
    {"key": "production", "label": "Виробництво"},
    {"key": "finance", "label": "Фінанси"},
    {"key": "reports", "label": "Звіти"},
    {"key": "settings", "label": "Адміністрування"},
    {"key": "dictionaries", "label": "Довідники"},
    {"key": "print_templates", "label": "Шаблони документів"},
    {"key": "business_processes", "label": "Бізнес-процеси"},
    {"key": "users", "label": "Користувачі"},
]

ROLE_OPTIONS = [
    {"value": "admin", "label": "Адміністратор"},
    {"value": "manager", "label": "Менеджер"},
    {"value": "production", "label": "Виробництво"},
    {"value": "warehouse", "label": "Склад"},
    {"value": "accountant", "label": "Бухгалтер"},
    {"value": "viewer", "label": "Тільки перегляд"},
]

ALL_ACTIONS = [action["key"] for action in PERMISSION_ACTIONS]

ROLE_PRESETS: Dict[str, Dict[str, List[str]]] = {
    "admin": {module["key"]: ALL_ACTIONS for module in PERMISSION_MODULES},
    "manager": {
        "crm": ["view", "create", "edit", "print", "export"],
        "sales": ["view", "create", "edit", "print", "export"],
        "inventory": ["view"],
        "reports": ["view", "export"],
        "dictionaries": ["view"],
    },
    "production": {
        "production": ["view", "create", "edit", "print"],
        "inventory": ["view", "import"],
        "crm": ["view"],
        "reports": ["view"],
    },
    "warehouse": {
        "inventory": ["view", "create", "edit", "import", "export"],
        "production": ["view"],
        "sales": ["view"],
        "reports": ["view"],
    },
    "accountant": {
        "finance": ["view", "create", "edit", "print", "export", "import"],
        "sales": ["view", "print", "export"],
        "reports": ["view", "print", "export"],
        "crm": ["view"],
    },
    "viewer": {module["key"]: ["view"] for module in PERMISSION_MODULES},
}

VALID_PERMISSION_KEYS = {
    f"{module['key']}.{action['key']}"
    for module in PERMISSION_MODULES
    for action in PERMISSION_ACTIONS
}


def permissions_registry_payload() -> dict:
    return {
        "modules": PERMISSION_MODULES,
        "actions": PERMISSION_ACTIONS,
        "roles": ROLE_OPTIONS,
        "role_presets": ROLE_PRESETS,
    }


def sanitize_permissions(permissions: dict | None) -> dict:
    if not permissions:
        return {}
    return {
        key: bool(value)
        for key, value in permissions.items()
        if key in VALID_PERMISSION_KEYS or key.endswith(".view")
    }


def role_permissions(role: str) -> dict:
    permissions = {}
    for module_key, actions in ROLE_PRESETS.get(role, {}).items():
        for action in actions:
            permissions[f"{module_key}.{action}"] = True
    return permissions


def has_permission(user, permission: str) -> bool:
    if not user:
        return False
    if user.is_superuser or user.role == "admin":
        return True

    permissions = user.permissions or {}
    if permissions.get(permission):
        return True

    parts = permission.split(".")
    module = parts[0]
    action = parts[-1] if len(parts) > 1 else "view"

    return bool(
        permissions.get(f"{module}.{action}")
        or permissions.get(f"{module}.manage")
        or permissions.get(f"{module}.view")
        or permissions.get(f"{module}.all")
    )
