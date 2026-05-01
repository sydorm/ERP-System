export const PERMISSION_ACTIONS = [
  { key: 'view', label: 'Перегляд' },
  { key: 'create', label: 'Створення' },
  { key: 'edit', label: 'Редагування' },
  { key: 'delete', label: 'Видалення' },
  { key: 'print', label: 'Друк' },
  { key: 'export', label: 'Експорт' },
  { key: 'import', label: 'Імпорт' },
  { key: 'manage', label: 'Керування' },
]

export const PERMISSION_MODULES = [
  { key: 'crm', label: 'CRM' },
  { key: 'inventory', label: 'Склад' },
  { key: 'sales', label: 'Продажі' },
  { key: 'production', label: 'Виробництво' },
  { key: 'finance', label: 'Фінанси' },
  { key: 'reports', label: 'Звіти' },
  { key: 'settings', label: 'Адміністрування' },
  { key: 'dictionaries', label: 'Довідники' },
  { key: 'print_templates', label: 'Шаблони документів' },
  { key: 'business_processes', label: 'Бізнес-процеси' },
  { key: 'users', label: 'Користувачі' },
  { key: 'personnel', label: 'Персонал' },
]

export const ROLE_OPTIONS = [
  { value: 'admin', label: 'Адміністратор' },
  { value: 'manager', label: 'Менеджер' },
  { value: 'production', label: 'Виробництво' },
  { value: 'warehouse', label: 'Склад' },
  { value: 'accountant', label: 'Бухгалтер' },
  { value: 'viewer', label: 'Тільки перегляд' },
]

const allActions = PERMISSION_ACTIONS.map(action => action.key)

export const ROLE_PRESETS = {
  admin: {
    modules: Object.fromEntries(PERMISSION_MODULES.map(module => [module.key, allActions])),
  },
  manager: {
    modules: {
      crm: ['view', 'create', 'edit', 'print', 'export'],
      sales: ['view', 'create', 'edit', 'print', 'export'],
      inventory: ['view'],
      reports: ['view', 'export'],
      dictionaries: ['view'],
    },
  },
  production: {
    modules: {
      production: ['view', 'create', 'edit', 'print'],
      inventory: ['view', 'import'],
      crm: ['view'],
      reports: ['view'],
    },
  },
  warehouse: {
    modules: {
      inventory: ['view', 'create', 'edit', 'import', 'export'],
      production: ['view'],
      sales: ['view'],
      reports: ['view'],
    },
  },
  accountant: {
    modules: {
      finance: ['view', 'create', 'edit', 'print', 'export', 'import'],
      sales: ['view', 'print', 'export'],
      reports: ['view', 'print', 'export'],
      crm: ['view'],
      personnel: ['view', 'create', 'edit', 'print', 'export'],
    },
  },
  viewer: {
    modules: Object.fromEntries(PERMISSION_MODULES.map(module => [module.key, ['view']])),
  },
}

export const buildPermissionGroups = () => PERMISSION_MODULES.map(module => ({
  ...module,
  all: false,
  items: PERMISSION_ACTIONS.map(action => ({
    ...action,
    key: `${module.key}.${action.key}`,
  })),
}))

export const buildPermissionsForRole = (role) => {
  const permissions = {}
  const preset = ROLE_PRESETS[role]?.modules || {}

  Object.entries(preset).forEach(([moduleKey, actions]) => {
    actions.forEach(action => {
      permissions[`${moduleKey}.${action}`] = true
    })
  })

  return permissions
}

export const syncPermissionGroups = (groups, permissions) => {
  groups.forEach(group => {
    group.all = group.items.every(item => Boolean(permissions[item.key]))
  })
}

export const setGroupPermissions = (permissions, group, value) => {
  group.items.forEach(item => {
    permissions[item.key] = value
  })
}

export const getRoleName = (role) => ROLE_OPTIONS.find(item => item.value === role)?.label || role
