import { Bell, Moon, Sun, Search, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface BreadcrumbItem {
  label: string;
  href?: string;
  active?: boolean;
}

interface HeaderProps {
  title: string;
  breadcrumbs: BreadcrumbItem[];
  onCreateClick?: () => void;
}

export function Header({ title, breadcrumbs, onCreateClick }: HeaderProps) {
  const [isDark, setIsDark] = useState(false);
  const [notifications] = useState(3);

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      {/* Top Bar */}
      <div className="h-12 px-4 flex items-center justify-between">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-2 text-sm">
          {breadcrumbs.map((item, index) => (
            <div key={item.label} className="flex items-center gap-2">
              {index > 0 && <ChevronRight className="w-4 h-4 text-slate-400" />}
              {item.active ? (
                <span className="font-medium text-slate-900">{item.label}</span>
              ) : (
                <a
                  href={item.href || '#'}
                  className="text-slate-500 hover:text-indigo-600 transition-colors"
                >
                  {item.label}
                </a>
              )}
            </div>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg">
            <Search className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-500">Ctrl + K</span>
          </div>

          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsDark(!isDark)}
            className="relative"
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-amber-500" />
            ) : (
              <Moon className="w-5 h-5 text-slate-600" />
            )}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-5 h-5 text-slate-600" />
            {notifications > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-rose-500 text-white text-xs font-medium rounded-full flex items-center justify-center">
                {notifications}
              </span>
            )}
          </Button>
        </div>
      </div>

      {/* Title Bar */}
      <div className="px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
          <p className="text-sm text-slate-500 mt-1">
            Керуйте вашими товарами та відстежуйте запаси
          </p>
        </div>

        {onCreateClick && (
          <Button
            onClick={onCreateClick}
            className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-200 transition-all duration-200 hover:shadow-lg hover:shadow-indigo-200"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Створити товар
          </Button>
        )}
      </div>

      {/* Tabs */}
      <div className="px-4 flex gap-1 border-t border-slate-200">
        {['Головна', 'Номенклатура', 'Склади'].map((tab, index) => (
          <button
            key={tab}
            className={cn(
              'px-3 py-2 text-xs font-medium border-b-2 transition-all duration-200 relative',
              index === 1
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
            )}
          >
            {tab}
            {index === 1 && (
              <button className="ml-2 text-slate-400 hover:text-slate-600">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </button>
        ))}
      </div>
    </header>
  );
}
