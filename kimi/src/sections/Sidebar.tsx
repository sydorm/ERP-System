import { 
  LayoutDashboard, 
  Package, 
  Boxes, 
  ShoppingCart, 
  Users, 
  Factory,
  TrendingDown,
  BarChart3,
  Settings,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';

export type ViewType = 
  | 'dashboard'
  | 'products'
  | 'product-create'
  | 'characteristics'
  | 'smart-bom'
  | 'pricing'
  | 'warehouses'
  | 'inventory'
  | 'sales-orders'
  | 'customers'
  | 'purchase-orders'
  | 'suppliers'
  | 'production-planning'
  | 'production-orders'
  | 'work-centers'
  | 'employees'
  | 'payroll'
  | 'payroll-types'
  | 'reports'
  | 'analytics'
  | 'settings'
  | 'company'
  | 'users';

interface MenuItem {
  icon: React.ElementType;
  label: string;
  view?: ViewType;
  children?: { label: string; view: ViewType }[];
}

interface SidebarProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

const menuItems: MenuItem[] = [
  { icon: LayoutDashboard, label: 'Головна', view: 'dashboard' },
  {
    icon: Package,
    label: 'Номенклатура',
    children: [
      { label: 'Товари', view: 'products' },
      { label: 'Характеристики', view: 'characteristics' },
      { label: 'Специфікації BOM', view: 'smart-bom' },
      { label: 'Ціноутворення', view: 'pricing' },
    ],
  },
  {
    icon: Boxes,
    label: 'Склад',
    children: [
      { label: 'Склади', view: 'warehouses' },
      { label: 'Залишки', view: 'inventory' },
    ],
  },
  {
    icon: ShoppingCart,
    label: 'Продажі',
    children: [
      { label: 'Замовлення', view: 'sales-orders' },
      { label: 'Клієнти', view: 'customers' },
    ],
  },
  {
    icon: TrendingDown,
    label: 'Закупівлі',
    children: [
      { label: 'Замовлення', view: 'purchase-orders' },
      { label: 'Постачальники', view: 'suppliers' },
    ],
  },
  {
    icon: Factory,
    label: 'Виробництво',
    children: [
      { label: 'Планування', view: 'production-planning' },
      { label: 'Виробничі замовлення', view: 'production-orders' },
      { label: 'Робочі центри', view: 'work-centers' },
    ],
  },
  {
    icon: Users,
    label: 'Персонал',
    children: [
      { label: 'Співробітники', view: 'employees' },
      { label: 'Нарахування ЗП', view: 'payroll' },
      { label: 'Види нарахувань', view: 'payroll-types' },
    ],
  },
  {
    icon: BarChart3,
    label: 'Звіти та аналітика',
    children: [
      { label: 'Звіти', view: 'reports' },
      { label: 'Аналітика', view: 'analytics' },
    ],
  },
  {
    icon: Settings,
    label: 'Налаштування',
    children: [
      { label: 'Компанія', view: 'company' },
      { label: 'Користувачі', view: 'users' },
    ],
  },
];

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const [expandedItems, setExpandedItems] = useState<string[]>([
    'Номенклатура', 'Виробництво', 'Персонал'
  ]);

  const toggleExpand = (label: string) => {
    setExpandedItems((prev) =>
      prev.includes(label) ? prev.filter((item) => item !== label) : [...prev, label]
    );
  };

  const isChildActive = (children?: { label: string; view: ViewType }[]) => {
    return children?.some(child => child.view === currentView) || false;
  };

  return (
    <aside className="w-56 bg-slate-900 text-slate-300 h-screen flex flex-col fixed left-0 top-0 z-40">
      {/* Logo */}
      <div className="h-12 flex items-center px-4 border-b border-slate-800">
        <Boxes className="w-6 h-6 text-indigo-500 mr-2" />
        <span className="text-lg font-bold text-white">ERP Pro</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-2">
        <ul className="space-y-0.5 px-2">
          {menuItems.map((item) => {
            const isExpanded = expandedItems.includes(item.label);
            const hasChildren = item.children && item.children.length > 0;
            const isActive = item.view === currentView || isChildActive(item.children);

            return (
              <li key={item.label}>
                <button
                  onClick={() => {
                    if (hasChildren) {
                      toggleExpand(item.label);
                    } else if (item.view) {
                      onViewChange(item.view);
                    }
                  }}
                  className={cn(
                    'w-full flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-medium transition-all duration-200',
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-400 border-l-2 border-indigo-500'
                      : 'hover:bg-slate-800 hover:text-white'
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {hasChildren && (
                    <span className="text-slate-500">
                      {isExpanded ? (
                        <ChevronDown className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5" />
                      )}
                    </span>
                  )}
                </button>

                {/* Submenu */}
                {hasChildren && isExpanded && item.children && (
                  <ul className="mt-0.5 ml-3 pl-3 border-l border-slate-700 space-y-0.5">
                    {item.children.map((child) => (
                      <li key={child.view}>
                        <button
                          onClick={() => onViewChange(child.view)}
                          className={cn(
                            'w-full text-left block px-2.5 py-1.5 rounded-md text-xs transition-all duration-200',
                            currentView === child.view
                              ? 'bg-indigo-600/30 text-indigo-300'
                              : 'text-slate-400 hover:text-white hover:bg-slate-800'
                          )}
                        >
                          {child.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800">
        <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-slate-800/50">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
            А
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-white truncate">Адміністратор</p>
            <p className="text-[10px] text-slate-500 truncate">admin@erp.pro</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
