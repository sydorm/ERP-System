import { Package, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface StatCard {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  trend?: string;
}

const stats: StatCard[] = [
  {
    title: 'Всього товарів',
    value: 2,
    icon: Package,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    trend: '+12%',
  },
  {
    title: 'В наявності',
    value: 0,
    icon: CheckCircle2,
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    trend: '0%',
  },
  {
    title: 'Закінчуються',
    value: 0,
    icon: AlertTriangle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    trend: '0%',
  },
  {
    title: 'Немає',
    value: 2,
    icon: XCircle,
    color: 'text-rose-600',
    bgColor: 'bg-rose-50',
    trend: '+2',
  },
];

export function StatsCards() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {stats.map((stat) => (
        <Card
          key={stat.title}
          className={cn(
            'relative overflow-hidden p-3 border-0 shadow-sm hover:shadow-md transition-all duration-300 group',
            'bg-white'
          )}
        >
          {/* Background decoration */}
          <div
            className={cn(
              'absolute -right-3 -top-3 w-16 h-16 rounded-full opacity-20 transition-transform duration-300 group-hover:scale-110',
              stat.bgColor
            )}
          />

          <div className="relative flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-500 mb-0.5 truncate">{stat.title}</p>
              <div className="flex items-baseline gap-1.5">
                <span className="text-xl font-bold text-slate-900">{stat.value}</span>
                {stat.trend && (
                  <span
                    className={cn(
                      'text-[10px] font-medium px-1.5 py-0.5 rounded-full',
                      stat.trend.startsWith('+')
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-slate-100 text-slate-600'
                    )}
                  >
                    {stat.trend}
                  </span>
                )}
              </div>
            </div>

            <div
              className={cn(
                'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110',
                stat.bgColor
              )}
            >
              <stat.icon className={cn('w-4 h-4', stat.color)} />
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-2">
            <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  stat.color.replace('text-', 'bg-')
                )}
                style={{
                  width: `${Math.min((stat.value / 10) * 100, 100)}%`,
                }}
              />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
