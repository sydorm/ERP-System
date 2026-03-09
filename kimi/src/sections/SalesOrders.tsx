import { useState, useEffect } from 'react';
import { 
  Plus, Search, Edit2, Trash2, Eye, FileText, DollarSign, CheckCircle2,
  Clock, XCircle, Truck, Printer, Package, RefreshCw, Filter
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { SalesOrderCreate } from './SalesOrderCreate';

type OrderStatus = 'draft' | 'confirmed' | 'in_production' | 'ready' | 'shipped' | 'delivered' | 'cancelled';
type PaymentStatus = 'pending' | 'partial' | 'paid';

interface OrderItem {
  id: string;
  productName: string;
  productSku: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

interface Customer {
  id: string;
  name: string;
  phone: string;
  email: string;
  address: string;
  discount: number;
  creditLimit: number;
  balance: number;
}

interface SalesOrder {
  id: string;
  number: string;
  date: string;
  customer: Customer | null;
  customerName: string;
  customerPhone: string;
  status: OrderStatus;
  paymentStatus: PaymentStatus;
  totalAmount: number;
  vatAmount: number;
  discountAmount: number;
  paidAmount: number;
  createdAt: string;
  updatedAt: string;
  deliveryDate?: string;
  items: OrderItem[];
  comment?: string;
}

const statusConfig: Record<OrderStatus, { label: string; color: string; icon: any }> = {
  draft: { label: 'Чернетка', color: 'bg-slate-100 text-slate-600', icon: FileText },
  confirmed: { label: 'Підтверджено', color: 'bg-blue-100 text-blue-600', icon: CheckCircle2 },
  in_production: { label: 'В виробництві', color: 'bg-amber-100 text-amber-600', icon: Clock },
  ready: { label: 'Готове', color: 'bg-emerald-100 text-emerald-600', icon: Package },
  shipped: { label: 'Відправлено', color: 'bg-indigo-100 text-indigo-600', icon: Truck },
  delivered: { label: 'Доставлено', color: 'bg-green-100 text-green-600', icon: CheckCircle2 },
  cancelled: { label: 'Скасовано', color: 'bg-rose-100 text-rose-600', icon: XCircle },
};

const paymentStatusConfig: Record<PaymentStatus, { label: string; color: string }> = {
  pending: { label: 'Не оплачено', color: 'bg-rose-100 text-rose-600' },
  partial: { label: 'Частково', color: 'bg-amber-100 text-amber-600' },
  paid: { label: 'Оплачено', color: 'bg-emerald-100 text-emerald-600' },
};

const initialOrders: SalesOrder[] = [
  {
    id: '1', number: 'ЗК-2024-001', date: '2024-03-01', customerName: 'ТОВ "Меблевий Світ"', customerPhone: '+380501234567',
    status: 'in_production', paymentStatus: 'partial', totalAmount: 45000, vatAmount: 7500, discountAmount: 5000, paidAmount: 22500,
    createdAt: '2024-03-01', updatedAt: '2024-03-01', deliveryDate: '2024-03-15',
    items: [
      { id: '1', productName: 'Стіл обідній "Лофт"', productSku: 'TABLE-001', quantity: 5, unitPrice: 5000, totalPrice: 25000 },
      { id: '2', productName: 'Стілець кухонний "Комфорт"', productSku: 'CHAIR-001', quantity: 10, unitPrice: 2000, totalPrice: 20000 },
    ],
    customer: { id: '1', name: 'ТОВ "Меблевий Світ"', phone: '+380501234567', email: 'info@meblisvit.ua', address: 'м. Київ, вул. Фабрична, 15', discount: 10, creditLimit: 200000, balance: -45000 }
  },
  {
    id: '2', number: 'ЗК-2024-002', date: '2024-03-02', customerName: 'Іванов Петро', customerPhone: '+380671112233',
    status: 'confirmed', paymentStatus: 'pending', totalAmount: 12500, vatAmount: 2083, discountAmount: 0, paidAmount: 0,
    createdAt: '2024-03-02', updatedAt: '2024-03-02', deliveryDate: '2024-03-10',
    items: [{ id: '1', productName: 'Консоль металева "Індустріал"', productSku: 'CONSOLE-001', quantity: 1, unitPrice: 12500, totalPrice: 12500 }],
    customer: { id: '2', name: 'Іванов Петро Сергійович', phone: '+380671112233', email: 'ivanov@email.com', address: 'м. Львів, вул. Шевченка, 42', discount: 0, creditLimit: 50000, balance: 0 }
  },
  {
    id: '3', number: 'ЗК-2024-003', date: '2024-03-03', customerName: 'ТОВ "Офіс Плюс"', customerPhone: '+380442223344',
    status: 'ready', paymentStatus: 'paid', totalAmount: 85000, vatAmount: 14167, discountAmount: 15000, paidAmount: 85000,
    createdAt: '2024-03-03', updatedAt: '2024-03-05', deliveryDate: '2024-03-12',
    items: [
      { id: '1', productName: 'Стіл письмовий "Бізнес"', productSku: 'DESK-001', quantity: 5, unitPrice: 12000, totalPrice: 60000 },
      { id: '2', productName: 'Офісне крісло "Ергономік"', productSku: 'CHAIR-OFF-001', quantity: 5, unitPrice: 8500, totalPrice: 42500 },
    ],
    customer: { id: '3', name: 'ТОВ "Офіс Плюс"', phone: '+380442223344', email: 'office@plus.ua', address: 'м. Київ, пр-т Перемоги, 100', discount: 15, creditLimit: 300000, balance: -120000 }
  },
  {
    id: '4', number: 'ЗК-2024-004', date: '2024-03-04', customerName: 'Сидорова Марія', customerPhone: '+380933334455',
    status: 'shipped', paymentStatus: 'paid', totalAmount: 3200, vatAmount: 533, discountAmount: 0, paidAmount: 3200,
    createdAt: '2024-03-04', updatedAt: '2024-03-06', deliveryDate: '2024-03-08',
    items: [{ id: '1', productName: 'Стілець банкетний "Елегант"', productSku: 'CHAIR-BAN-001', quantity: 1, unitPrice: 3200, totalPrice: 3200 }],
    customer: { id: '4', name: 'Сидорова Марія Олегівна', phone: '+380933334455', email: 'sidorova@email.com', address: 'м. Одеса, вул. Дерибасівська, 25', discount: 5, creditLimit: 30000, balance: -8500 }
  },
  {
    id: '5', number: 'ЗК-2024-005', date: '2024-03-05', customerName: 'ТОВ "Ресторан Гранд"', customerPhone: '+380504445566',
    status: 'draft', paymentStatus: 'pending', totalAmount: 56000, vatAmount: 9333, discountAmount: 14000, paidAmount: 0,
    createdAt: '2024-03-05', updatedAt: '2024-03-05', deliveryDate: '2024-03-20',
    items: [
      { id: '1', productName: 'Стіл банкетний "Преміум"', productSku: 'TABLE-BAN-001', quantity: 5, unitPrice: 8000, totalPrice: 40000 },
      { id: '2', productName: 'Стілець банкетний "Елегант"', productSku: 'CHAIR-BAN-001', quantity: 10, unitPrice: 3200, totalPrice: 32000 },
    ],
    customer: { id: '5', name: 'ТОВ "Ресторан Гранд"', phone: '+380504445566', email: 'grand@restaurant.ua', address: 'м. Дніпро, пр-т Гагаріна, 88', discount: 20, creditLimit: 150000, balance: -25000 }
  },
];

export function SalesOrders() {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);

  // Load orders from localStorage on mount
  useEffect(() => {
    const savedOrders = localStorage.getItem('erp_orders');
    if (savedOrders) {
      const parsed = JSON.parse(savedOrders);
      // Merge with initial orders
      const merged = [...initialOrders];
      parsed.forEach((o: SalesOrder) => {
        if (!merged.find(mo => mo.id === o.id)) {
          merged.push(o);
        }
      });
      setOrders(merged);
    } else {
      setOrders(initialOrders);
      localStorage.setItem('erp_orders', JSON.stringify(initialOrders));
    }
  }, []);

  // Refresh orders when returning from create form
  useEffect(() => {
    if (!showCreateForm) {
      const savedOrders = localStorage.getItem('erp_orders');
      if (savedOrders) {
        setOrders(JSON.parse(savedOrders));
      }
    }
  }, [showCreateForm]);

  const handleDeleteOrder = (orderId: string) => {
    const updatedOrders = orders.filter(o => o.id !== orderId);
    setOrders(updatedOrders);
    localStorage.setItem('erp_orders', JSON.stringify(updatedOrders));
    toast.success('Замовлення видалено');
  };

  const handleEditOrder = (order: SalesOrder) => {
    setSelectedOrder(order);
    setShowCreateForm(true);
  };

  const handleViewOrder = (order: SalesOrder) => {
    setSelectedOrder(order);
    setIsViewDialogOpen(true);
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.number.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.customerPhone.includes(searchQuery);
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalAmount = orders.reduce((sum, o) => sum + o.totalAmount, 0);
  const totalPending = orders.filter(o => o.status !== 'delivered' && o.status !== 'cancelled').length;
  const totalCompleted = orders.filter(o => o.status === 'delivered').length;

  if (showCreateForm) {
    return <SalesOrderCreate onBack={() => { setShowCreateForm(false); setSelectedOrder(null); }} orderToEdit={selectedOrder as any} />;
  }

  return (
    <div className="space-y-3">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-3">
        <Card className="p-3 bg-gradient-to-br from-indigo-50 to-white border-indigo-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Всього замовлень</p>
              <p className="text-xl font-bold text-indigo-600">{orders.length}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3 bg-gradient-to-br from-emerald-50 to-white border-emerald-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Загальна сума</p>
              <p className="text-xl font-bold text-emerald-600">{totalAmount.toLocaleString()} ₴</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-emerald-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3 bg-gradient-to-br from-amber-50 to-white border-amber-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">В роботі</p>
              <p className="text-xl font-bold text-amber-600">{totalPending}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
              <Clock className="w-5 h-5 text-amber-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3 bg-gradient-to-br from-blue-50 to-white border-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500">Виконано</p>
              <p className="text-xl font-bold text-blue-600">{totalCompleted}</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input 
              placeholder="Пошук за номером, клієнтом або телефоном..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-9 text-sm"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40 h-9 text-sm">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Всі статуси" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Всі статуси</SelectItem>
              <SelectItem value="draft">Чернетка</SelectItem>
              <SelectItem value="confirmed">Підтверджено</SelectItem>
              <SelectItem value="in_production">В виробництві</SelectItem>
              <SelectItem value="ready">Готове</SelectItem>
              <SelectItem value="shipped">Відправлено</SelectItem>
              <SelectItem value="delivered">Доставлено</SelectItem>
              <SelectItem value="cancelled">Скасовано</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" className="h-9" onClick={() => {
            const saved = localStorage.getItem('erp_orders');
            if (saved) setOrders(JSON.parse(saved));
            toast.success('Дані оновлено');
          }}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
        <Button size="sm" className="h-9 text-xs bg-indigo-600 hover:bg-indigo-700" onClick={() => setShowCreateForm(true)}>
          <Plus className="w-4 h-4 mr-1" /> Нове замовлення
        </Button>
      </div>

      {/* Orders Table */}
      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50">
              <TableHead className="text-xs w-10">№</TableHead>
              <TableHead className="text-xs">Номер / Дата</TableHead>
              <TableHead className="text-xs">Клієнт</TableHead>
              <TableHead className="text-xs text-center">Статус</TableHead>
              <TableHead className="text-xs text-center">Оплата</TableHead>
              <TableHead className="text-xs text-right">Сума</TableHead>
              <TableHead className="text-xs text-center">Доставка</TableHead>
              <TableHead className="text-xs w-32 text-center">Дії</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredOrders.map((order, index) => {
              const StatusIcon = statusConfig[order.status].icon;
              return (
                <TableRow key={order.id} className="hover:bg-slate-50">
                  <TableCell className="text-xs text-slate-400">{index + 1}</TableCell>
                  <TableCell>
                    <div>
                      <p className="text-sm font-medium text-indigo-600">{order.number}</p>
                      <p className="text-[10px] text-slate-400">{order.date}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="text-sm font-medium">{order.customerName}</p>
                      <p className="text-[10px] text-slate-400">{order.customerPhone}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge className={cn('text-[10px]', statusConfig[order.status].color)}>
                      <StatusIcon className="w-3 h-3 mr-1" />
                      {statusConfig[order.status].label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge className={cn('text-[10px]', paymentStatusConfig[order.paymentStatus].color)}>
                      {paymentStatusConfig[order.paymentStatus].label}
                    </Badge>
                    {order.paidAmount > 0 && (
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        {order.paidAmount.toLocaleString()} / {order.totalAmount.toLocaleString()} ₴
                      </p>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <p className="text-sm font-medium">{order.totalAmount.toLocaleString()} ₴</p>
                    {order.discountAmount > 0 && (
                      <p className="text-[10px] text-emerald-600">- {order.discountAmount.toLocaleString()} ₴</p>
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    {order.deliveryDate ? (
                      <span className="text-xs">{order.deliveryDate}</span>
                    ) : (
                      <span className="text-xs text-slate-400">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center justify-center gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleViewOrder(order)}>
                        <Eye className="w-4 h-4 text-slate-400" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleEditOrder(order)}>
                        <Edit2 className="w-4 h-4 text-indigo-400" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => toast.info('Друк замовлення')}>
                        <Printer className="w-4 h-4 text-slate-400" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDeleteOrder(order.id)}>
                        <Trash2 className="w-4 h-4 text-rose-400" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
            {filteredOrders.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8">
                  <Package className="w-12 h-12 text-slate-200 mx-auto mb-2" />
                  <p className="text-sm text-slate-500">Замовлення не знайдено</p>
                  <Button variant="outline" size="sm" className="mt-2" onClick={() => setShowCreateForm(true)}>
                    <Plus className="w-4 h-4 mr-1" /> Створити замовлення
                  </Button>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      {/* View Order Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-base">Замовлення {selectedOrder?.number}</DialogTitle>
          </DialogHeader>
          {selectedOrder && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500">Клієнт</p>
                  <p className="text-sm font-medium">{selectedOrder.customerName}</p>
                  <p className="text-xs text-slate-400">{selectedOrder.customerPhone}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Дата доставки</p>
                  <p className="text-sm">{selectedOrder.deliveryDate || 'Не вказана'}</p>
                </div>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-2">Товари</p>
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="h-8 bg-slate-50">
                        <TableHead className="text-xs">Товар</TableHead>
                        <TableHead className="text-xs text-center">К-ть</TableHead>
                        <TableHead className="text-xs text-right">Ціна</TableHead>
                        <TableHead className="text-xs text-right">Сума</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedOrder.items.map((item) => (
                        <TableRow key={item.id} className="h-9">
                          <TableCell>
                            <p className="text-sm">{item.productName}</p>
                            <p className="text-[10px] text-slate-400">{item.productSku}</p>
                          </TableCell>
                          <TableCell className="text-center text-sm">{item.quantity}</TableCell>
                          <TableCell className="text-right text-sm">{item.unitPrice.toLocaleString()} ₴</TableCell>
                          <TableCell className="text-right text-sm font-medium">{item.totalPrice.toLocaleString()} ₴</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
              <div className="flex justify-between items-center pt-2 border-t">
                <div>
                  <p className="text-xs text-slate-500">Статус</p>
                  <Badge className={cn('text-[10px] mt-1', statusConfig[selectedOrder.status].color)}>
                    {statusConfig[selectedOrder.status].label}
                  </Badge>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500">Всього</p>
                  <p className="text-xl font-bold text-indigo-600">{selectedOrder.totalAmount.toLocaleString()} ₴</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
