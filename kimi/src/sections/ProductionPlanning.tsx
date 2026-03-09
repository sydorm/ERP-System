import { useState } from 'react';
import { 
  ArrowLeft, 
  Plus, 
  Calendar, 
  Factory,
  CheckCircle2,
  AlertCircle,
  Play,
  Pause,
  Check,
  MoreHorizontal,
  Search,
  BarChart3,
  Package,
  Printer,
  Download
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
// import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

// Статуси виробничих замовлень
type OrderStatus = 'planned' | 'in_progress' | 'paused' | 'completed' | 'cancelled';

interface ProductionOrder {
  id: string;
  number: string;
  productName: string;
  productSku: string;
  quantity: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: OrderStatus;
  plannedStart: string;
  plannedEnd: string;
  actualStart?: string;
  actualEnd?: string;
  department: string;
  assignedTo?: string;
  progress: number;
  estimatedHours: number;
  actualHours?: number;
}

interface WorkCenter {
  id: string;
  name: string;
  department: string;
  capacity: number;
  currentLoad: number;
  efficiency: number;
}

const productionOrders: ProductionOrder[] = [
  {
    id: '1',
    number: 'ВЗ-2024-001',
    productName: 'Стіл обідній "Лофт"',
    productSku: 'TABLE-LOFT-001',
    quantity: 10,
    priority: 'high',
    status: 'in_progress',
    plannedStart: '2024-03-08',
    plannedEnd: '2024-03-12',
    actualStart: '2024-03-08',
    department: 'Металообробка',
    assignedTo: 'Іванов П.',
    progress: 65,
    estimatedHours: 40,
    actualHours: 26,
  },
  {
    id: '2',
    number: 'ВЗ-2024-002',
    productName: 'Полиць настінна',
    productSku: 'SHELF-WALL-002',
    quantity: 25,
    priority: 'medium',
    status: 'planned',
    plannedStart: '2024-03-10',
    plannedEnd: '2024-03-14',
    department: 'Деревообробка',
    progress: 0,
    estimatedHours: 30,
  },
  {
    id: '3',
    number: 'ВЗ-2024-003',
    productName: 'Консоль металева',
    productSku: 'CONSOLE-MET-003',
    quantity: 5,
    priority: 'urgent',
    status: 'in_progress',
    plannedStart: '2024-03-07',
    plannedEnd: '2024-03-09',
    actualStart: '2024-03-07',
    department: 'Металообробка',
    assignedTo: 'Петров С.',
    progress: 80,
    estimatedHours: 16,
    actualHours: 12.8,
  },
  {
    id: '4',
    number: 'ВЗ-2024-004',
    productName: 'Стілець кухонний',
    productSku: 'CHAIR-KIT-004',
    quantity: 50,
    priority: 'low',
    status: 'planned',
    plannedStart: '2024-03-15',
    plannedEnd: '2024-03-22',
    department: 'Збірка',
    progress: 0,
    estimatedHours: 75,
  },
  {
    id: '5',
    number: 'ВЗ-2024-005',
    productName: 'Стіл письмовий',
    productSku: 'TABLE-DESK-005',
    quantity: 8,
    priority: 'medium',
    status: 'completed',
    plannedStart: '2024-03-01',
    plannedEnd: '2024-03-05',
    actualStart: '2024-03-01',
    actualEnd: '2024-03-04',
    department: 'Деревообробка',
    assignedTo: 'Сидоров М.',
    progress: 100,
    estimatedHours: 32,
    actualHours: 30,
  },
];

const workCenters: WorkCenter[] = [
  { id: '1', name: 'Лазерний різак TRUMPF', department: 'Розкрій', capacity: 8, currentLoad: 6, efficiency: 92 },
  { id: '2', name: 'Гнутик CNC', department: 'Гнуття', capacity: 8, currentLoad: 7, efficiency: 88 },
  { id: '3', name: 'Зварювальний пост 1', department: 'Зварювання', capacity: 8, currentLoad: 5, efficiency: 95 },
  { id: '4', name: 'Зварювальний пост 2', department: 'Зварювання', capacity: 8, currentLoad: 4, efficiency: 90 },
  { id: '5', name: 'Фарбувальна камера', department: 'Фарбування', capacity: 8, currentLoad: 6, efficiency: 85 },
  { id: '6', name: 'Фрезерний станок', department: 'Деревообробка', capacity: 8, currentLoad: 3, efficiency: 94 },
  { id: '7', name: 'Лінія збірки', department: 'Збірка', capacity: 8, currentLoad: 5, efficiency: 91 },
];

const statusConfig: Record<OrderStatus, { label: string; color: string; icon: any }> = {
  planned: { label: 'Заплановано', color: 'bg-slate-100 text-slate-700', icon: Calendar },
  in_progress: { label: 'В роботі', color: 'bg-blue-100 text-blue-700', icon: Play },
  paused: { label: 'Призупинено', color: 'bg-amber-100 text-amber-700', icon: Pause },
  completed: { label: 'Виконано', color: 'bg-emerald-100 text-emerald-700', icon: Check },
  cancelled: { label: 'Скасовано', color: 'bg-rose-100 text-rose-700', icon: AlertCircle },
};

const priorityConfig = {
  low: { label: 'Низький', color: 'bg-slate-100 text-slate-600' },
  medium: { label: 'Середній', color: 'bg-blue-100 text-blue-600' },
  high: { label: 'Високий', color: 'bg-amber-100 text-amber-600' },
  urgent: { label: 'Терміновий', color: 'bg-rose-100 text-rose-600' },
};

export function ProductionPlanning({ onBack }: { onBack: () => void }) {
  const [orders, setOrders] = useState<ProductionOrder[]>(productionOrders);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isNewOrderOpen, setIsNewOrderOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'kanban' | 'gantt'>('list');

  const filteredOrders = orders.filter(order => {
    const matchesStatus = selectedStatus === 'all' || order.status === selectedStatus;
    const matchesSearch = 
      order.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.productSku.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const stats = {
    total: orders.length,
    planned: orders.filter(o => o.status === 'planned').length,
    inProgress: orders.filter(o => o.status === 'in_progress').length,
    completed: orders.filter(o => o.status === 'completed').length,
  };

  const handleStatusChange = (orderId: string, newStatus: OrderStatus) => {
    setOrders(prev => prev.map(o => 
      o.id === orderId ? { ...o, status: newStatus } : o
    ));
    toast.success(`Статус замовлення оновлено`);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onBack} className="h-8 w-8">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Планування виробництва</h2>
            <p className="text-xs text-slate-500">Управління виробничими замовленнями</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Printer className="w-3.5 h-3.5 mr-1.5" />
            Друк
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-3.5 h-3.5 mr-1.5" />
            Експорт
          </Button>
          <Dialog open={isNewOrderOpen} onOpenChange={setIsNewOrderOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">
                <Plus className="w-3.5 h-3.5 mr-1.5" />
                Нове замовлення
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-base">Нове виробниче замовлення</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label className="text-xs">Продукт</Label>
                  <Select>
                    <SelectTrigger className="h-9 text-sm">
                      <SelectValue placeholder="Оберіть продукт" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Стіл обідній "Лофт"</SelectItem>
                      <SelectItem value="2">Полиць настінна</SelectItem>
                      <SelectItem value="3">Консоль металева</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label className="text-xs">Кількість</Label>
                    <Input type="number" placeholder="1" className="h-9 text-sm" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs">Пріоритет</Label>
                    <Select>
                      <SelectTrigger className="h-9 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Низький</SelectItem>
                        <SelectItem value="medium">Середній</SelectItem>
                        <SelectItem value="high">Високий</SelectItem>
                        <SelectItem value="urgent">Терміновий</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label className="text-xs">Плановий початок</Label>
                    <Input type="date" className="h-9 text-sm" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs">Планове завершення</Label>
                    <Input type="date" className="h-9 text-sm" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">Відповідальний</Label>
                  <Select>
                    <SelectTrigger className="h-9 text-sm">
                      <SelectValue placeholder="Оберіть працівника" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Іванов П.</SelectItem>
                      <SelectItem value="2">Петров С.</SelectItem>
                      <SelectItem value="3">Сидоров М.</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsNewOrderOpen(false)}>
                  Скасувати
                </Button>
                <Button 
                  onClick={() => {
                    toast.success('Виробниче замовлення створено');
                    setIsNewOrderOpen(false);
                  }}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  Створити
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-3">
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Всього замовлень</p>
              <p className="text-xl font-bold text-slate-900">{stats.total}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
              <Package className="w-5 h-5 text-slate-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Заплановано</p>
              <p className="text-xl font-bold text-slate-600">{stats.planned}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
              <Calendar className="w-5 h-5 text-slate-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">В роботі</p>
              <p className="text-xl font-bold text-blue-600">{stats.inProgress}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <Play className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Виконано</p>
              <p className="text-xl font-bold text-emerald-600">{stats.completed}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            </div>
          </div>
        </Card>
      </div>

      <Tabs defaultValue="orders" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="orders" className="text-xs">
            <Package className="w-3.5 h-3.5 mr-1.5" />
            Замовлення
          </TabsTrigger>
          <TabsTrigger value="workcenters" className="text-xs">
            <Factory className="w-3.5 h-3.5 mr-1.5" />
            Робочі центри
          </TabsTrigger>
          <TabsTrigger value="schedule" className="text-xs">
            <Calendar className="w-3.5 h-3.5 mr-1.5" />
            Графік
          </TabsTrigger>
        </TabsList>

        <TabsContent value="orders" className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-xs">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input 
                placeholder="Пошук замовлень..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 h-9 text-sm"
              />
            </div>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="h-9 text-sm w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Всі статуси</SelectItem>
                <SelectItem value="planned">Заплановано</SelectItem>
                <SelectItem value="in_progress">В роботі</SelectItem>
                <SelectItem value="completed">Виконано</SelectItem>
                <SelectItem value="cancelled">Скасовано</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex items-center gap-1 ml-auto">
              <Button 
                variant={viewMode === 'list' ? 'default' : 'outline'} 
                size="icon" 
                className="h-9 w-9"
                onClick={() => setViewMode('list')}
              >
                <Package className="w-4 h-4" />
              </Button>
              <Button 
                variant={viewMode === 'kanban' ? 'default' : 'outline'} 
                size="icon" 
                className="h-9 w-9"
                onClick={() => setViewMode('kanban')}
              >
                <BarChart3 className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Orders Table */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50">
                  <tr className="h-9">
                    <th className="px-3 text-left text-xs font-medium text-slate-600">Номер</th>
                    <th className="px-3 text-left text-xs font-medium text-slate-600">Продукт</th>
                    <th className="px-3 text-center text-xs font-medium text-slate-600">К-ть</th>
                    <th className="px-3 text-center text-xs font-medium text-slate-600">Пріоритет</th>
                    <th className="px-3 text-center text-xs font-medium text-slate-600">Статус</th>
                    <th className="px-3 text-left text-xs font-medium text-slate-600">Терміни</th>
                    <th className="px-3 text-left text-xs font-medium text-slate-600">Виконавець</th>
                    <th className="px-3 text-center text-xs font-medium text-slate-600">Прогрес</th>
                    <th className="px-3 text-right text-xs font-medium text-slate-600 w-24">Дії</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.map(order => {
                    const StatusIcon = statusConfig[order.status].icon;
                    return (
                      <tr key={order.id} className="border-t hover:bg-slate-50 h-12">
                        <td className="px-3">
                          <span className="text-sm font-medium">{order.number}</span>
                        </td>
                        <td className="px-3">
                          <div>
                            <p className="text-sm font-medium">{order.productName}</p>
                            <p className="text-[10px] text-slate-400">{order.productSku}</p>
                          </div>
                        </td>
                        <td className="px-3 text-center">
                          <span className="text-sm">{order.quantity}</span>
                        </td>
                        <td className="px-3 text-center">
                          <Badge className={cn('text-[10px]', priorityConfig[order.priority].color)}>
                            {priorityConfig[order.priority].label}
                          </Badge>
                        </td>
                        <td className="px-3 text-center">
                          <Badge className={cn('text-[10px]', statusConfig[order.status].color)}>
                            <StatusIcon className="w-3 h-3 mr-1" />
                            {statusConfig[order.status].label}
                          </Badge>
                        </td>
                        <td className="px-3">
                          <div className="text-xs">
                            <p>{order.plannedStart} - {order.plannedEnd}</p>
                            {order.actualStart && (
                              <p className="text-slate-400">Факт: {order.actualStart}</p>
                            )}
                          </div>
                        </td>
                        <td className="px-3">
                          <span className="text-sm">{order.assignedTo || '-'}</span>
                        </td>
                        <td className="px-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                              <div 
                                className={cn(
                                  'h-full rounded-full transition-all',
                                  order.progress === 100 ? 'bg-emerald-500' : 'bg-blue-500'
                                )}
                                style={{ width: `${order.progress}%` }}
                              />
                            </div>
                            <span className="text-xs w-8">{order.progress}%</span>
                          </div>
                        </td>
                        <td className="px-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            {order.status === 'planned' && (
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-7 w-7"
                                onClick={() => handleStatusChange(order.id, 'in_progress')}
                              >
                                <Play className="w-3.5 h-3.5 text-emerald-500" />
                              </Button>
                            )}
                            {order.status === 'in_progress' && (
                              <>
                                <Button 
                                  variant="ghost" 
                                  size="icon" 
                                  className="h-7 w-7"
                                  onClick={() => handleStatusChange(order.id, 'paused')}
                                >
                                  <Pause className="w-3.5 h-3.5 text-amber-500" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="icon" 
                                  className="h-7 w-7"
                                  onClick={() => handleStatusChange(order.id, 'completed')}
                                >
                                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                                </Button>
                              </>
                            )}
                            <Button variant="ghost" size="icon" className="h-7 w-7">
                              <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="workcenters" className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {workCenters.map(wc => (
              <Card key={wc.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="text-sm font-semibold">{wc.name}</h4>
                    <p className="text-xs text-slate-500">{wc.department}</p>
                  </div>
                  <Badge className={cn(
                    'text-[10px]',
                    wc.currentLoad / wc.capacity > 0.9 ? 'bg-rose-100 text-rose-700' :
                    wc.currentLoad / wc.capacity > 0.7 ? 'bg-amber-100 text-amber-700' :
                    'bg-emerald-100 text-emerald-700'
                  )}>
                    {Math.round((wc.currentLoad / wc.capacity) * 100)}%
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Завантаження:</span>
                    <span>{wc.currentLoad} / {wc.capacity} год</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div 
                      className={cn(
                        'h-full rounded-full transition-all',
                        wc.currentLoad / wc.capacity > 0.9 ? 'bg-rose-500' :
                        wc.currentLoad / wc.capacity > 0.7 ? 'bg-amber-500' :
                        'bg-emerald-500'
                      )}
                      style={{ width: `${(wc.currentLoad / wc.capacity) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Ефективність:</span>
                    <span className="font-medium">{wc.efficiency}%</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="schedule" className="space-y-4">
          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-4">Виробничий графік (тиждень)</h3>
            <div className="space-y-3">
              {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'].map((day, i) => (
                <div key={day} className="flex items-center gap-3">
                  <div className="w-10 text-sm font-medium text-slate-500">{day}</div>
                  <div className="flex-1 h-8 bg-slate-100 rounded-lg relative overflow-hidden">
                    {i < 4 && (
                      <>
                        <div 
                          className="absolute h-full bg-blue-400 rounded-l-lg"
                          style={{ left: '10%', width: '25%' }}
                        />
                        <div 
                          className="absolute h-full bg-emerald-400"
                          style={{ left: '40%', width: '20%' }}
                        />
                      </>
                    )}
                    {i === 4 && (
                      <div 
                        className="absolute h-full bg-amber-400 rounded-lg"
                        style={{ left: '15%', width: '30%' }}
                      />
                    )}
                  </div>
                  <div className="w-16 text-right text-xs text-slate-500">
                    {i < 4 ? '8/8 год' : i === 4 ? '6/8 год' : '0/8 год'}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
