import { useState, useMemo, useEffect, useCallback } from 'react';
import { 
  Plus, Search, Trash2, Save, CheckCircle2, ArrowLeft, Calculator, Truck, CreditCard,
  Factory, FileText, History, Sparkles, Package, User, MapPin, Phone, Mail,
  TrendingUp, AlertTriangle, Check, ChevronDown, Copy, Printer, Send, Boxes,
  Wrench, Clock, BarChart3, Zap, Settings2, MoreHorizontal, Eye, Download,
  Receipt, Edit3, UserPlus
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

// Types
interface OrderItem {
  id: string; productId: string; productName: string; productSku: string;
  characteristic?: string; quantity: number; reserved: number; unitPrice: number;
  discount: number; totalPrice: number; vatRate: number; vatAmount: number;
  specification?: string; isService: boolean; productionRequired: boolean;
  stockQuantity: number; minPrice: number; costPrice: number;
}

interface Customer {
  id: string; name: string; phone: string; email: string; address: string;
  discount: number; creditLimit: number; balance: number; edrpou?: string; contactPerson?: string;
}

interface DeliveryInfo {
  method: 'self' | 'courier' | 'np_branch' | 'np_courier' | 'truck';
  address: string; branchNumber?: string; recipientName: string; recipientPhone: string;
  desiredDate: string; desiredTime: string; cost: number; trackingNumber?: string;
}

interface PaymentRecord {
  id: string; date: string; amount: number; method: string;
  status: 'pending' | 'completed' | 'cancelled';
}

interface PaymentInfo {
  method: 'cash' | 'card' | 'bank_transfer' | 'credit' | 'installment';
  prepayment: number; installmentMonths?: number; dueDate: string; payments: PaymentRecord[];
}

interface AIRecommendation {
  type: 'stock' | 'price' | 'delivery' | 'production' | 'customer';
  message: string; severity: 'info' | 'warning' | 'success'; action?: string;
}

interface ProductionTask {
  id: string; itemId: string; productName: string; quantity: number;
  deadline: string; status: 'pending' | 'planned' | 'in_progress' | 'completed';
  materialsReserved: boolean; workCenter?: string; assignedTo?: string;
}

interface OrderDocument {
  id: string; type: 'invoice' | 'waybill' | 'production_order' | 'power_of_attorney' | 'contract';
  number: string; date: string; status: 'draft' | 'issued' | 'sent' | 'paid'; amount?: number;
}

interface OrderHistoryRecord {
  id: string; date: string; user: string; action: string;
  details?: string; oldValue?: string; newValue?: string;
}

interface SalesOrder {
  id: string; number: string; date: string;
  status: 'draft' | 'confirmed' | 'in_production' | 'ready' | 'shipped' | 'delivered' | 'cancelled';
  customer: Customer | null; items: OrderItem[]; delivery: DeliveryInfo; payment: PaymentInfo;
  comment: string; productionTasks: ProductionTask[]; documents: OrderDocument[]; history: OrderHistoryRecord[];
  totalAmount: number; vatAmount: number; discountAmount: number;
  createdAt: string; updatedAt: string; createdBy: string;
}

// Mock Data
const customers: Customer[] = [
  { id: '1', name: 'ТОВ "Меблевий Світ"', phone: '+380501234567', email: 'info@meblisvit.ua', address: 'м. Київ, вул. Фабрична, 15', discount: 10, creditLimit: 200000, balance: -45000, edrpou: '12345678', contactPerson: 'Іванов І.І.' },
  { id: '2', name: 'Іванов Петро Сергійович', phone: '+380671112233', email: 'ivanov@email.com', address: 'м. Львів, вул. Шевченка, 42', discount: 0, creditLimit: 50000, balance: 0, contactPerson: 'Іванов П.С.' },
  { id: '3', name: 'ТОВ "Офіс Плюс"', phone: '+380442223344', email: 'office@plus.ua', address: 'м. Київ, пр-т Перемоги, 100', discount: 15, creditLimit: 300000, balance: -120000, edrpou: '87654321', contactPerson: 'Петрова О.О.' },
  { id: '4', name: 'Сидорова Марія Олегівна', phone: '+380933334455', email: 'sidorova@email.com', address: 'м. Одеса, вул. Дерибасівська, 25', discount: 5, creditLimit: 30000, balance: -8500 },
  { id: '5', name: 'ТОВ "Ресторан Гранд"', phone: '+380504445566', email: 'grand@restaurant.ua', address: 'м. Дніпро, пр-т Гагаріна, 88', discount: 20, creditLimit: 150000, balance: -25000, edrpou: '11223344', contactPerson: 'Сидоренко Г.Г.' },
];

const products = [
  { id: '1', name: 'Стіл обідній "Лофт"', sku: 'TABLE-001', price: 5000, costPrice: 2800, stock: 3, minPrice: 4000, weight: 25 },
  { id: '2', name: 'Стілець кухонний "Комфорт"', sku: 'CHAIR-001', price: 2000, costPrice: 1100, stock: 15, minPrice: 1600, weight: 8 },
  { id: '3', name: 'Консоль металева "Індустріал"', sku: 'CONSOLE-001', price: 12500, costPrice: 7000, stock: 2, minPrice: 10000, weight: 35 },
  { id: '4', name: 'Стіл письмовий "Бізнес"', sku: 'DESK-001', price: 12000, costPrice: 6500, stock: 5, minPrice: 9600, weight: 40 },
  { id: '5', name: 'Офісне крісло "Ергономік"', sku: 'CHAIR-OFF-001', price: 8500, costPrice: 4800, stock: 8, minPrice: 6800, weight: 18 },
  { id: '6', name: 'Полиця настінна "Мінімал"', sku: 'SHELF-001', price: 2500, costPrice: 1300, stock: 20, minPrice: 2000, weight: 5 },
  { id: '7', name: 'Кронштейн металевий', sku: 'BRACKET-001', price: 500, costPrice: 200, stock: 100, minPrice: 350, weight: 1 },
  { id: '8', name: 'Стіл банкетний "Преміум"', sku: 'TABLE-BAN-001', price: 8000, costPrice: 4500, stock: 0, minPrice: 6400, productionDays: 7, weight: 30 },
  { id: '9', name: 'Стілець банкетний "Елегант"', sku: 'CHAIR-BAN-001', price: 3200, costPrice: 1800, stock: 12, minPrice: 2560, weight: 9 },
  { id: '10', name: 'Шафа офісна "Стандарт"', sku: 'CABINET-001', price: 15000, costPrice: 8500, stock: 0, minPrice: 12000, productionDays: 10, weight: 55 },
];

const characteristics: Record<string, string[]> = {
  'TABLE-001': ['Дуб натуральний', 'Горіх темний', 'Білий матовий'],
  'CHAIR-001': ['Сірий', 'Бежевий', 'Чорний'],
  'CONSOLE-001': ['Чорний метал', 'Білий метал', 'Золото'],
  'DESK-001': ['Дуб', 'Горіх', 'Бук'],
  'CHAIR-OFF-001': ['Чорна шкіра', 'Сіра тканина', 'Коричнева шкіра'],
  'SHELF-001': ['Білий', 'Чорний', 'Дерево'],
  'TABLE-BAN-001': ['Дуб', 'Ясен', 'Горіх'],
  'CHAIR-BAN-001': ['Золото + оксамит', 'Срібло + шкіра', 'Бронза + тканина'],
  'CABINET-001': ['Дуб натуральний', 'Білий глянець', 'Графіт'],
};

const workCenters = [
  { id: 'wc1', name: 'Деревообробка', capacity: 8 },
  { id: 'wc2', name: 'Металообробка', capacity: 6 },
  { id: 'wc3', name: 'Фарбування', capacity: 4 },
  { id: 'wc4', name: 'Збірка', capacity: 10 },
  { id: 'wc5', name: 'Пакування', capacity: 5 },
];

// AI Helper Functions
const generateAIRecommendations = (items: OrderItem[], customer: Customer | null, totalAmount: number, deliveryInfo: DeliveryInfo): AIRecommendation[] => {
  const recommendations: AIRecommendation[] = [];
  items.forEach(item => {
    if (item.stockQuantity < item.quantity && !item.isService) {
      recommendations.push({ type: 'stock', message: `"${item.productName}" - недостатньо на складі. Потрібно: ${item.quantity}, в наявності: ${item.stockQuantity}`, severity: 'warning', action: 'Запустити в виробництво' });
    }
    if (item.unitPrice < item.minPrice) {
      recommendations.push({ type: 'price', message: `Ціна на "${item.productName}" (${item.unitPrice} ₴) нижче мінімальної (${item.minPrice} ₴)`, severity: 'warning', action: 'Переглянути ціну' });
    }
  });
  if (customer) {
    if (customer.balance < 0 && Math.abs(customer.balance) + totalAmount > customer.creditLimit) {
      recommendations.push({ type: 'customer', message: `Клієнт перевищить кредитний ліміт (${customer.creditLimit.toLocaleString()} ₴)`, severity: 'warning', action: 'Вимагати передоплату' });
    }
    if (customer.discount > 0) {
      recommendations.push({ type: 'customer', message: `Клієнт має постійну знижку ${customer.discount}%`, severity: 'info' });
    }
  }
  const totalCost = items.reduce((sum, item) => sum + (item.costPrice * item.quantity), 0);
  const margin = totalAmount > 0 ? ((totalAmount - totalCost) / totalAmount) * 100 : 0;
  if (margin < 15) recommendations.push({ type: 'price', message: `Маржа критично низька (${margin.toFixed(1)}%)!`, severity: 'warning' });
  else if (margin > 40) recommendations.push({ type: 'price', message: `Відмінна маржа (${margin.toFixed(1)}%)!`, severity: 'success' });
  if (items.length > 0 && !deliveryInfo.address && deliveryInfo.method !== 'self') {
    recommendations.push({ type: 'delivery', message: 'Не вказана адреса доставки', severity: 'warning', action: 'Заповнити адресу' });
  }
  return recommendations;
};

const calculateProductionDays = (items: OrderItem[]): number => {
  let maxDays = 0;
  items.forEach(item => {
    const product = products.find(p => p.id === item.productId);
    if (product && product.productionDays && item.stockQuantity < item.quantity) {
      maxDays = Math.max(maxDays, product.productionDays);
    }
  });
  return maxDays;
};

const calculateDeliveryCost = (method: string, weight: number): number => {
  const rates: Record<string, number> = { self: 0, courier: 150, np_branch: weight * 15 + 50, np_courier: weight * 20 + 100, truck: weight * 8 + 500 };
  return Math.round(rates[method] || 0);
};

// Helper icon component
function BarcodeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 5v14" /><path d="M8 5v14" /><path d="M12 5v14" /><path d="M17 5v14" /><path d="M21 5v14" />
    </svg>
  );
}


// Main Component
export function SalesOrderCreate({ onBack, orderToEdit }: { onBack: () => void; orderToEdit?: SalesOrder }) {
  const [activeTab, setActiveTab] = useState('items');
  const [orderNumber, setOrderNumber] = useState(orderToEdit?.number || '');
  const [orderDate, setOrderDate] = useState(orderToEdit?.date || new Date().toISOString().split('T')[0]);
  const [status, setStatus] = useState(orderToEdit?.status || 'draft');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(orderToEdit?.customer || null);
  const [items, setItems] = useState<OrderItem[]>(orderToEdit?.items || []);
  const [delivery, setDelivery] = useState<DeliveryInfo>(orderToEdit?.delivery || { method: 'self', address: '', recipientName: '', recipientPhone: '', desiredDate: '', desiredTime: '', cost: 0 });
  const [payment, setPayment] = useState<PaymentInfo>(orderToEdit?.payment || { method: 'bank_transfer', prepayment: 0, dueDate: '', payments: [] });
  const [comment, setComment] = useState(orderToEdit?.comment || '');
  const [productionTasks, setProductionTasks] = useState<ProductionTask[]>(orderToEdit?.productionTasks || []);
  const [documents, setDocuments] = useState<OrderDocument[]>(orderToEdit?.documents || []);
  const [history, setHistory] = useState<OrderHistoryRecord[]>(orderToEdit?.history || []);
  
  const [showProductDialog, setShowProductDialog] = useState(false);
  const [searchProductQuery, setSearchProductQuery] = useState('');
  const [showCustomerDialog, setShowCustomerDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showPrintDialog, setShowPrintDialog] = useState(false);
  const [newPaymentAmount, setNewPaymentAmount] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!orderNumber) {
      const savedOrders = localStorage.getItem('erp_orders');
      const orders = savedOrders ? JSON.parse(savedOrders) : [];
      const nextNumber = orders.length + 6;
      setOrderNumber(`ЗК-2024-${String(nextNumber).padStart(3, '0')}`);
    }
  }, []);

  useEffect(() => {
    const totalWeight = items.reduce((sum, item) => {
      const product = products.find(p => p.id === item.productId);
      return sum + (item.quantity * (product?.weight || 5));
    }, 0);
    const cost = calculateDeliveryCost(delivery.method, totalWeight);
    setDelivery(prev => ({ ...prev, cost }));
  }, [delivery.method, items]);

  const subtotal = useMemo(() => items.reduce((sum, item) => sum + item.totalPrice, 0), [items]);
  const vatTotal = useMemo(() => items.reduce((sum, item) => sum + item.vatAmount, 0), [items]);
  const discountTotal = useMemo(() => items.reduce((sum, item) => sum + ((item.unitPrice * item.quantity * item.discount / 100)), 0), [items]);
  const totalAmount = subtotal;
  const totalWeight = useMemo(() => items.reduce((sum, item) => { const product = products.find(p => p.id === item.productId); return sum + (item.quantity * (product?.weight || 5)); }, 0), [items]);
  const paidAmount = useMemo(() => payment.payments.filter(p => p.status === 'completed').reduce((sum, p) => sum + p.amount, 0), [payment.payments]);
  const remainingAmount = totalAmount + delivery.cost - paidAmount;
  const aiRecommendations = useMemo(() => generateAIRecommendations(items, selectedCustomer, totalAmount, delivery), [items, selectedCustomer, totalAmount, delivery]);
  const productionDays = useMemo(() => calculateProductionDays(items), [items]);
  const needsProduction = items.some(item => item.productionRequired);

  const addHistoryRecord = useCallback((action: string, details?: string, oldValue?: string, newValue?: string) => {
    const record: OrderHistoryRecord = { id: Date.now().toString(), date: new Date().toISOString(), user: 'Адміністратор', action, details, oldValue, newValue };
    setHistory(prev => [record, ...prev]);
  }, []);

  const handleAddItem = (productId: string) => {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    const basePrice = selectedCustomer ? Math.round(product.price * (1 - selectedCustomer.discount / 100)) : product.price;
    const newItem: OrderItem = {
      id: Date.now().toString() + Math.random(), productId: product.id, productName: product.name, productSku: product.sku,
      characteristic: characteristics[product.sku]?.[0] || '', quantity: 1, reserved: 0, unitPrice: basePrice,
      discount: selectedCustomer?.discount || 0, totalPrice: basePrice, vatRate: 20, vatAmount: Math.round(basePrice * 0.2),
      specification: '', isService: false, productionRequired: product.stock < 1 && !!product.productionDays,
      stockQuantity: product.stock, minPrice: product.minPrice, costPrice: product.costPrice
    };
    setItems(prev => [...prev, newItem]);
    setShowProductDialog(false);
    setSearchProductQuery('');
    addHistoryRecord('Додано товар', `${product.name} (1 шт)`);
    toast.success(`Товар "${product.name}" додано`);
  };

  const handleUpdateItem = (id: string, updates: Partial<OrderItem>) => {
    setItems(prev => prev.map(item => {
      if (item.id !== id) return item;
      const updated = { ...item, ...updates };
      if (updates.quantity !== undefined || updates.unitPrice !== undefined || updates.discount !== undefined) {
        const qty = updates.quantity !== undefined ? updates.quantity : item.quantity;
        const price = updates.unitPrice !== undefined ? updates.unitPrice : item.unitPrice;
        const disc = updates.discount !== undefined ? updates.discount : item.discount;
        const basePrice = price * qty;
        const discountAmount = basePrice * (disc / 100);
        updated.totalPrice = Math.round(basePrice - discountAmount);
        updated.vatAmount = Math.round(updated.totalPrice * (updated.vatRate / 100));
      }
      return updated;
    }));
  };

  const handleRemoveItem = (id: string) => {
    const item = items.find(i => i.id === id);
    setItems(prev => prev.filter(item => item.id !== id));
    if (item) { addHistoryRecord('Видалено товар', item.productName); toast.info(`Товар "${item.productName}" видалено`); }
  };

  const handleCustomerChange = (customerId: string) => {
    const customer = customers.find(c => c.id === customerId);
    setSelectedCustomer(customer || null);
    if (customer) {
      setDelivery(prev => ({ ...prev, address: customer.address, recipientName: customer.contactPerson || customer.name, recipientPhone: customer.phone }));
      setItems(prev => prev.map(item => {
        const product = products.find(p => p.id === item.productId);
        if (!product) return item;
        const newUnitPrice = Math.round(product.price * (1 - customer.discount / 100));
        const basePrice = newUnitPrice * item.quantity;
        const discountAmount = basePrice * (customer.discount / 100);
        return { ...item, unitPrice: newUnitPrice, discount: customer.discount, totalPrice: Math.round(basePrice - discountAmount), vatAmount: Math.round((basePrice - discountAmount) * 0.2) };
      }));
      addHistoryRecord('Обрано покупця', customer.name);
      toast.success(`Покупця "${customer.name}" обрано`);
    }
    setShowCustomerDialog(false);
  };

  const handleReserveItem = (itemId: string, checked: boolean) => {
    const item = items.find(i => i.id === itemId);
    if (!item) return;
    const reserveQty = checked ? Math.min(item.quantity, item.stockQuantity) : 0;
    handleUpdateItem(itemId, { reserved: reserveQty });
    if (checked && reserveQty > 0) toast.success(`Зарезервовано ${reserveQty} шт. товару "${item.productName}"`);
  };

  const handleAddPayment = () => {
    const amount = parseFloat(newPaymentAmount);
    if (!amount || amount <= 0) { toast.error('Введіть коректну суму платежу'); return; }
    if (amount > remainingAmount) { toast.error('Сума платежу не може перевищувати залишок до оплати'); return; }
    const newPayment: PaymentRecord = { id: Date.now().toString(), date: new Date().toISOString().split('T')[0], amount, method: payment.method === 'cash' ? 'Готівка' : payment.method === 'card' ? 'Картка' : payment.method === 'bank_transfer' ? 'Банківський переказ' : 'Інше', status: 'completed' };
    setPayment(prev => ({ ...prev, payments: [...prev.payments, newPayment], prepayment: prev.prepayment + amount }));
    addHistoryRecord('Додано платіж', `Сума: ${amount.toLocaleString()} ₴`);
    setNewPaymentAmount(''); setShowPaymentDialog(false);
    toast.success(`Платіж на суму ${amount.toLocaleString()} ₴ додано`);
  };

  const handleCreateProductionTasks = () => {
    const tasks: ProductionTask[] = items.filter(item => item.productionRequired).map(item => ({
      id: Date.now().toString() + item.id, itemId: item.id, productName: item.productName, quantity: item.quantity,
      deadline: delivery.desiredDate || new Date(Date.now() + productionDays * 86400000).toISOString().split('T')[0],
      status: 'pending', materialsReserved: false, workCenter: workCenters[3].name
    }));
    setProductionTasks(tasks);
    const prodDoc: OrderDocument = { id: Date.now().toString(), type: 'production_order', number: `ВЗ-${orderNumber.split('-')[2]}`, date: new Date().toISOString().split('T')[0], status: 'issued' };
    setDocuments(prev => [...prev, prodDoc]);
    addHistoryRecord('Створено виробничі завдання', `${tasks.length} завдань`);
    toast.success(`Створено ${tasks.length} виробничих завдань`);
  };

  const handleCreateInvoice = () => {
    const invoice: OrderDocument = { id: Date.now().toString(), type: 'invoice', number: `РХ-${orderNumber.split('-')[2]}`, date: new Date().toISOString().split('T')[0], status: 'issued', amount: totalAmount + delivery.cost };
    setDocuments(prev => [...prev, invoice]);
    addHistoryRecord('Створено рахунок', invoice.number);
    toast.success(`Рахунок ${invoice.number} створено`);
  };

  const handleCreateWaybill = () => {
    const waybill: OrderDocument = { id: Date.now().toString(), type: 'waybill', number: `НВ-${orderNumber.split('-')[2]}`, date: new Date().toISOString().split('T')[0], status: 'draft' };
    setDocuments(prev => [...prev, waybill]);
    addHistoryRecord('Створено накладну', waybill.number);
    toast.success(`Накладна ${waybill.number} створено`);
  };

  const handleSaveOrder = async (post = false) => {
    if (items.length === 0) { toast.error('Додайте хоча б один товар'); return; }
    if (!selectedCustomer) { toast.error('Оберіть покупця'); return; }
    setIsSaving(true);
    try {
      const order: SalesOrder = {
        id: orderToEdit?.id || Date.now().toString(), number: orderNumber, date: orderDate, status: post ? 'confirmed' : 'draft',
        customer: selectedCustomer, items, delivery, payment, comment, productionTasks, documents, history,
        totalAmount, vatAmount: vatTotal, discountAmount: discountTotal,
        createdAt: orderToEdit?.createdAt || new Date().toISOString(), updatedAt: new Date().toISOString(), createdBy: 'Адміністратор'
      };
      const savedOrders = localStorage.getItem('erp_orders');
      const orders: SalesOrder[] = savedOrders ? JSON.parse(savedOrders) : [];
      if (orderToEdit) { const index = orders.findIndex(o => o.id === orderToEdit.id); if (index >= 0) orders[index] = order; else orders.push(order); }
      else orders.push(order);
      localStorage.setItem('erp_orders', JSON.stringify(orders));
      addHistoryRecord(post ? 'Замовлення проведено' : 'Замовлення збережено');
      toast.success(post ? 'Замовлення проведено та збережено' : 'Замовлення збережено як чернетку');
      if (post) setStatus('confirmed');
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) { toast.error('Помилка збереження замовлення'); }
    finally { setIsSaving(false); }
  };

  const handlePrint = (docType: string) => { toast.info(`Друк ${docType}...`); setShowPrintDialog(false); };
  const handleDuplicateOrder = () => {
    const newNumber = `ЗК-2024-${String(parseInt(orderNumber.split('-')[2]) + 1).padStart(3, '0')}`;
    setOrderNumber(newNumber); setStatus('draft'); setDocuments([]); setHistory([]); setProductionTasks([]); setPayment(prev => ({ ...prev, payments: [], prepayment: 0 }));
    addHistoryRecord('Замовлення скопійовано', `Новий номер: ${newNumber}`);
    toast.success('Замовлення скопійовано з новим номером');
  };
  const handleSendEmail = () => { if (!selectedCustomer?.email) { toast.error('У клієнта не вказано email'); return; } toast.success(`Пропозиція надіслана на ${selectedCustomer.email}`); };
  const filteredProducts = products.filter(p => p.name.toLowerCase().includes(searchProductQuery.toLowerCase()) || p.sku.toLowerCase().includes(searchProductQuery.toLowerCase()));

  return (
    <div className="h-full flex flex-col bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={onBack} className="h-8"><ArrowLeft className="w-4 h-4 mr-1" /> Назад</Button>
            <div>
              <h1 className="text-lg font-semibold">Замовлення покупця ({orderToEdit ? 'редагування' : 'створення'})</h1>
              <div className="flex items-center gap-2 text-xs text-slate-500"><span>Головна</span><span>/</span><span>Замовлення</span><span>/</span><span className="text-indigo-600">{orderNumber}</span></div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => handleSaveOrder(false)} disabled={isSaving}><Save className="w-3.5 h-3.5 mr-1" /> {isSaving ? 'Збереження...' : 'Записати'}</Button>
            <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => handleSaveOrder(true)} disabled={isSaving}><Check className="w-3.5 h-3.5 mr-1" /> Провести</Button>
            <Button size="sm" className="h-8 text-xs bg-indigo-600 hover:bg-indigo-700" onClick={() => handleSaveOrder(true)} disabled={isSaving}><CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Провести та закрити</Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild><Button variant="ghost" size="icon" className="h-8 w-8"><MoreHorizontal className="w-4 h-4" /></Button></DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleDuplicateOrder}><Copy className="w-4 h-4 mr-2" /> Копіювати</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setShowPrintDialog(true)}><Printer className="w-4 h-4 mr-2" /> Друк</DropdownMenuItem>
                <DropdownMenuItem onClick={handleSendEmail}><Send className="w-4 h-4 mr-2" /> Надіслати email</DropdownMenuItem>
                <DropdownMenuItem onClick={() => toast.info('Експорт в Excel')}><Download className="w-4 h-4 mr-2" /> Експорт в Excel</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-4 space-y-4">
            {/* Order Header */}
            <Card className="shadow-sm">
              <CardContent className="p-4">
                <div className="grid grid-cols-12 gap-4">
                  <div className="col-span-2">
                    <Label className="text-xs text-slate-500">Стан</Label>
                    <Select value={status} onValueChange={(val) => { setStatus(val as any); addHistoryRecord('Змінено статус'); }}>
                      <SelectTrigger className="h-8 text-sm mt-1"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Чернетка</SelectItem><SelectItem value="confirmed">Підтверджено</SelectItem><SelectItem value="in_production">В виробництві</SelectItem>
                        <SelectItem value="ready">Готове до відвантаження</SelectItem><SelectItem value="shipped">Відправлено</SelectItem><SelectItem value="delivered">Доставлено</SelectItem><SelectItem value="cancelled">Скасовано</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="col-span-2"><Label className="text-xs text-slate-500">Номер</Label><Input value={orderNumber} onChange={(e) => setOrderNumber(e.target.value)} className="h-8 text-sm mt-1" /></div>
                  <div className="col-span-2"><Label className="text-xs text-slate-500">від</Label><Input type="date" value={orderDate} onChange={(e) => setOrderDate(e.target.value)} className="h-8 text-sm mt-1" /></div>
                  <div className="col-span-6">
                    <Label className="text-xs text-slate-500">Покупець</Label>
                    <div className="flex gap-2 mt-1">
                      <Dialog open={showCustomerDialog} onOpenChange={setShowCustomerDialog}>
                        <DialogTrigger asChild><Button variant="outline" className="flex-1 justify-start h-8 text-sm">{selectedCustomer ? selectedCustomer.name : 'Оберіть покупця'}</Button></DialogTrigger>
                        <DialogContent className="max-w-lg">
                          <DialogHeader><DialogTitle>Оберіть покупця</DialogTitle></DialogHeader>
                          <div className="space-y-2 mt-4">
                            <Button variant="outline" className="w-full justify-start" onClick={() => toast.info('Форма нового клієнта')}><UserPlus className="w-4 h-4 mr-2" /> + Новий клієнт</Button>
                            {customers.map(c => (<Button key={c.id} variant="ghost" className="w-full justify-start h-auto py-3" onClick={() => handleCustomerChange(c.id)}><div className="text-left"><p className="font-medium">{c.name}</p><p className="text-xs text-slate-500">{c.phone} • {c.discount > 0 ? `Знижка ${c.discount}%` : 'Без знижки'}</p></div></Button>))}
                          </div>
                        </DialogContent>
                      </Dialog>
                      {selectedCustomer && (
                        <TooltipProvider><Tooltip><TooltipTrigger asChild><Button variant="outline" size="icon" className="h-8 w-8"><User className="w-4 h-4" /></Button></TooltipTrigger><TooltipContent className="max-w-xs"><div className="text-xs space-y-1"><p><strong>{selectedCustomer.name}</strong></p><p>📞 {selectedCustomer.phone}</p><p>✉️ {selectedCustomer.email}</p><p>📍 {selectedCustomer.address}</p>{selectedCustomer.edrpou && <p>🆔 ЄДРПОУ: {selectedCustomer.edrpou}</p>}<p>💳 Кредитний ліміт: {selectedCustomer.creditLimit.toLocaleString()} ₴</p><p className={selectedCustomer.balance < 0 ? 'text-rose-500' : 'text-emerald-500'}>Баланс: {selectedCustomer.balance.toLocaleString()} ₴</p></div></TooltipContent></Tooltip></TooltipProvider>
                      )}
                    </div>
                  </div>
                </div>
                {selectedCustomer && (
                  <div className="mt-3 p-2 bg-slate-50 rounded text-xs flex items-center gap-4 flex-wrap">
                    <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> {selectedCustomer.phone}</span>
                    <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> {selectedCustomer.email}</span>
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {selectedCustomer.address}</span>
                    <Badge variant="outline" className="text-[10px] ml-auto">Кредитний ліміт: {selectedCustomer.creditLimit.toLocaleString()} ₴</Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="w-full justify-start bg-white border rounded-lg p-1 h-auto flex-wrap">
                <TabsTrigger value="items" className="text-xs data-[state=active]:bg-indigo-50 data-[state=active]:text-indigo-600"><Package className="w-3.5 h-3.5 mr-1" /> Товари {items.length > 0 && <Badge className="ml-1 text-[10px] h-4 bg-indigo-100 text-indigo-600">{items.length}</Badge>}</TabsTrigger>
                <TabsTrigger value="delivery" className="text-xs data-[state=active]:bg-indigo-50 data-[state=active]:text-indigo-600"><Truck className="w-3.5 h-3.5 mr-1" /> Доставка {delivery.cost > 0 && <Badge className="ml-1 text-[10px] h-4 bg-emerald-100 text-emerald-600">{delivery.cost} ₴</Badge>}</TabsTrigger>
                <TabsTrigger value="payment" className="text-xs data-[state=active]:bg-indigo-50 data-[state=active]:text-indigo-600"><CreditCard className="w-3.5 h-3.5 mr-1" /> Оплата {paidAmount > 0 && <Badge className={cn("ml-1 text-[10px] h-4", paidAmount >= totalAmount ? "bg-emerald-100 text-emerald-600" : "bg-amber-100 text-amber-600")}>{paidAmount.toLocaleString()} ₴</Badge>}</TabsTrigger>
                <TabsTrigger value="production" className="text-xs data-[state=active]:bg-indigo-50 data-[state=active]:text-indigo-600"><Factory className="w-3.5 h-3.5 mr-1" /> Виробництво {productionTasks.length > 0 ? <Badge className="ml-1 text-[10px] h-4 bg-indigo-100 text-indigo-600">{productionTasks.length}</Badge> : needsProduction && <Badge className="ml-1 text-[10px] h-4 bg-amber-100 text-amber-600">!</Badge>}</TabsTrigger>
                <TabsTrigger value="documents" className="text-xs data-[state=active]:bg-indigo-50 data-[state=active]:text-indigo-600"><FileText className="w-3.5 h-3.5 mr-1" /> Документи {documents.length > 0 && <Badge className="ml-1 text-[10px] h-4 bg-indigo-100 text-indigo-600">{documents.length}</Badge>}</TabsTrigger>
                <TabsTrigger value="history" className="text-xs data-[state=active]:bg-indigo-50 data-[state=active]:text-indigo-600"><History className="w-3.5 h-3.5 mr-1" /> Історія {history.length > 0 && <Badge className="ml-1 text-[10px] h-4 bg-slate-100 text-slate-600">{history.length}</Badge>}</TabsTrigger>
              </TabsList>

              {/* Items Tab */}
              <TabsContent value="items" className="mt-4 space-y-4">
                <Card className="shadow-sm">
                  <CardContent className="p-0">
                    <div className="flex items-center gap-2 p-3 border-b bg-slate-50 flex-wrap">
                      <Dialog open={showProductDialog} onOpenChange={setShowProductDialog}>
                        <DialogTrigger asChild><Button size="sm" className="h-7 text-xs bg-indigo-600 hover:bg-indigo-700"><Plus className="w-3.5 h-3.5 mr-1" /> Додати</Button></DialogTrigger>
                        <DialogContent className="max-w-2xl max-h-[80vh]">
                          <DialogHeader><DialogTitle className="text-base">Додати товар</DialogTitle></DialogHeader>
                          <div className="space-y-4 py-4">
                            <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" /><Input placeholder="Пошук товару..." value={searchProductQuery} onChange={(e) => setSearchProductQuery(e.target.value)} className="pl-10" autoFocus /></div>
                            <div className="border rounded-lg overflow-hidden">
                              <Table>
                                <TableHeader><TableRow className="h-8 bg-slate-50"><TableHead className="text-xs">Товар</TableHead><TableHead className="text-xs text-right">Ціна</TableHead><TableHead className="text-xs text-center">Наявність</TableHead><TableHead className="text-xs text-center"></TableHead></TableRow></TableHeader>
                                <TableBody>
                                  {filteredProducts.map(product => (
                                    <TableRow key={product.id} className="h-10">
                                      <TableCell><div><p className="text-sm font-medium">{product.name}</p><p className="text-[10px] text-slate-400">{product.sku}</p></div></TableCell>
                                      <TableCell className="text-right"><p className="text-sm">{product.price.toLocaleString()} ₴</p><p className="text-[10px] text-slate-400">Собівартість: {product.costPrice.toLocaleString()} ₴</p></TableCell>
                                      <TableCell className="text-center"><Badge className={cn('text-[10px]', product.stock > 5 ? 'bg-emerald-100 text-emerald-600' : product.stock > 0 ? 'bg-amber-100 text-amber-600' : 'bg-rose-100 text-rose-600')}>{product.stock > 0 ? `${product.stock} шт` : 'Під замовлення'}</Badge></TableCell>
                                      <TableCell className="text-center"><Button size="sm" className="h-7 text-xs" onClick={() => handleAddItem(product.id)}><Plus className="w-3.5 h-3.5" /></Button></TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                      <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => toast.info('Сканер штрих-коду')}><BarcodeIcon className="w-3.5 h-3.5 mr-1" /> Сканер</Button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild><Button variant="outline" size="sm" className="h-7 text-xs"><Settings2 className="w-3.5 h-3.5 mr-1" /> Дії <ChevronDown className="w-3 h-3 ml-1" /></Button></DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem onClick={() => toast.info('Функція в розробці')}><Copy className="w-4 h-4 mr-2" /> Копіювати з іншого замовлення</DropdownMenuItem>
                          <DropdownMenuItem onClick={() => toast.info('Функція в розробці')}><TrendingUp className="w-4 h-4 mr-2" /> Імпорт з Excel</DropdownMenuItem>
                          <DropdownMenuItem onClick={() => { setItems([]); addHistoryRecord('Очищено список товарів'); toast.info('Список товарів очищено'); }}><Trash2 className="w-4 h-4 mr-2" /> Очистити все</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                      <div className="ml-auto flex items-center gap-2"><Label className="text-xs text-slate-500">Склад:</Label><Select defaultValue="main"><SelectTrigger className="h-7 text-xs w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="main">Основний склад</SelectItem><SelectItem value="production">Виробництво</SelectItem><SelectItem value="retail">Роздріб</SelectItem></SelectContent></Select></div>
                    </div>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader><TableRow className="bg-slate-50 h-8"><TableHead className="text-xs w-8">№</TableHead><TableHead className="text-xs">Номенклатура</TableHead><TableHead className="text-xs w-32">Характеристика</TableHead><TableHead className="text-xs w-20 text-center">К-ть</TableHead><TableHead className="text-xs w-16 text-center">Резерв</TableHead><TableHead className="text-xs w-24 text-right">Ціна</TableHead><TableHead className="text-xs w-16 text-center">Знижка %</TableHead><TableHead className="text-xs w-24 text-right">Сума</TableHead><TableHead className="text-xs w-24">Спец.</TableHead><TableHead className="text-xs w-8"></TableHead></TableRow></TableHeader>
                        <TableBody>
                          {items.map((item, index) => (
                            <TableRow key={item.id} className="h-12">
                              <TableCell className="text-xs text-slate-400">{index + 1}</TableCell>
                              <TableCell>
                                <div><p className="text-sm font-medium">{item.productName}</p><p className="text-[10px] text-slate-400">{item.productSku}</p>{item.productionRequired && <Badge className="text-[10px] h-4 bg-amber-100 text-amber-600 mt-0.5"><Wrench className="w-3 h-3 mr-0.5" /> Потребує виробництва</Badge>}</div>
                              </TableCell>
                              <TableCell><Select value={item.characteristic} onValueChange={(val) => handleUpdateItem(item.id, { characteristic: val })}><SelectTrigger className="h-7 text-xs"><SelectValue /></SelectTrigger><SelectContent>{characteristics[item.productSku]?.map(char => <SelectItem key={char} value={char} className="text-xs">{char}</SelectItem>)}</SelectContent></Select></TableCell>
                              <TableCell><Input type="number" value={item.quantity} onChange={(e) => handleUpdateItem(item.id, { quantity: parseInt(e.target.value) || 0 })} className="h-7 text-xs text-center" min={1} /></TableCell>
                              <TableCell className="text-center"><Checkbox checked={item.reserved > 0} onCheckedChange={(checked) => handleReserveItem(item.id, checked as boolean)} disabled={item.stockQuantity === 0} />{item.reserved > 0 && <p className="text-[10px] text-emerald-600 mt-0.5">{item.reserved}</p>}</TableCell>
                              <TableCell><Input type="number" value={item.unitPrice} onChange={(e) => handleUpdateItem(item.id, { unitPrice: parseInt(e.target.value) || 0 })} className={cn("h-7 text-xs text-right", item.unitPrice < item.minPrice && "border-rose-300 bg-rose-50")} />{item.unitPrice < item.minPrice && <p className="text-[10px] text-rose-500">Мін: {item.minPrice} ₴</p>}</TableCell>
                              <TableCell><Input type="number" value={item.discount} onChange={(e) => handleUpdateItem(item.id, { discount: parseInt(e.target.value) || 0 })} className="h-7 text-xs text-center" min={0} max={100} /></TableCell>
                              <TableCell className="text-right"><p className="text-sm font-medium">{item.totalPrice.toLocaleString()} ₴</p><p className="text-[10px] text-slate-400">ПДВ: {item.vatAmount.toLocaleString()} ₴</p></TableCell>
                              <TableCell><Input placeholder="..." value={item.specification} onChange={(e) => handleUpdateItem(item.id, { specification: e.target.value })} className="h-7 text-xs" /></TableCell>
                              <TableCell><Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleRemoveItem(item.id)}><Trash2 className="w-4 h-4 text-rose-400" /></Button></TableCell>
                            </TableRow>
                          ))}
                          {items.length === 0 && <TableRow><TableCell colSpan={10} className="text-center py-8"><Package className="w-12 h-12 text-slate-200 mx-auto mb-2" /><p className="text-sm text-slate-500">Додайте товари до замовлення</p><Button variant="outline" size="sm" className="mt-2" onClick={() => setShowProductDialog(true)}><Plus className="w-4 h-4 mr-1" /> Додати товар</Button></TableCell></TableRow>}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
                <div className="flex gap-4"><div className="flex-1"><Label className="text-xs text-slate-500 mb-1">Коментар</Label><Textarea placeholder="Додаткова інформація про замовлення..." value={comment} onChange={(e) => setComment(e.target.value)} className="min-h-[60px] text-sm resize-none" /></div></div>
              </TabsContent>


              {/* Delivery Tab */}
              <TabsContent value="delivery" className="mt-4 space-y-4">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><Truck className="w-4 h-4" /> Інформація про доставку</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <Label className="text-xs text-slate-500">Спосіб доставки</Label>
                        <Select value={delivery.method} onValueChange={(val: any) => { setDelivery(prev => ({ ...prev, method: val })); addHistoryRecord('Змінено спосіб доставки', val); }}>
                          <SelectTrigger className="h-8 text-sm mt-1"><SelectValue /></SelectTrigger>
                          <SelectContent><SelectItem value="self">Самовивіз</SelectItem><SelectItem value="courier">Кур'єр</SelectItem><SelectItem value="np_branch">Нова Пошта (відділення)</SelectItem><SelectItem value="np_courier">Нова Пошта (кур'єр)</SelectItem><SelectItem value="truck">Вантажний транспорт</SelectItem></SelectContent>
                        </Select>
                      </div>
                      <div><Label className="text-xs text-slate-500">Бажана дата</Label><Input type="date" value={delivery.desiredDate} onChange={(e) => setDelivery(prev => ({ ...prev, desiredDate: e.target.value }))} className="h-8 text-sm mt-1" /></div>
                      <div><Label className="text-xs text-slate-500">Бажаний час</Label><Input type="time" value={delivery.desiredTime} onChange={(e) => setDelivery(prev => ({ ...prev, desiredTime: e.target.value }))} className="h-8 text-sm mt-1" /></div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div><Label className="text-xs text-slate-500">Отримувач</Label><Input value={delivery.recipientName} onChange={(e) => setDelivery(prev => ({ ...prev, recipientName: e.target.value }))} placeholder="ПІБ отримувача" className="h-8 text-sm mt-1" /></div>
                      <div><Label className="text-xs text-slate-500">Телефон</Label><Input value={delivery.recipientPhone} onChange={(e) => setDelivery(prev => ({ ...prev, recipientPhone: e.target.value }))} placeholder="+380..." className="h-8 text-sm mt-1" /></div>
                    </div>
                    <div><Label className="text-xs text-slate-500">Адреса доставки</Label><Textarea value={delivery.address} onChange={(e) => setDelivery(prev => ({ ...prev, address: e.target.value }))} placeholder="Введіть повну адресу..." className="min-h-[60px] text-sm mt-1 resize-none" /></div>
                    {delivery.method === 'np_branch' && <div><Label className="text-xs text-slate-500">Номер відділення</Label><Input value={delivery.branchNumber} onChange={(e) => setDelivery(prev => ({ ...prev, branchNumber: e.target.value }))} placeholder="№ відділення" className="h-8 text-sm mt-1 w-40" /></div>}
                    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2"><Boxes className="w-4 h-4 text-slate-400" /><span className="text-sm">Вага: <span className="font-medium">{totalWeight} кг</span></span></div>
                        <div className="flex items-center gap-2"><Package className="w-4 h-4 text-slate-400" /><span className="text-sm">Об'єм: <span className="font-medium">{(totalWeight * 0.05).toFixed(2)} м³</span></span></div>
                      </div>
                      <div className="flex items-center gap-2"><span className="text-sm text-slate-500">Доставка:</span><Input type="number" value={delivery.cost} onChange={(e) => setDelivery(prev => ({ ...prev, cost: parseInt(e.target.value) || 0 }))} className="h-7 text-sm w-24 text-right" /><span className="text-sm">₴</span></div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Payment Tab */}
              <TabsContent value="payment" className="mt-4 space-y-4">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><CreditCard className="w-4 h-4" /> Умови оплати</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-3 gap-4">
                      <div><Label className="text-xs text-slate-500">Спосіб оплати</Label><Select value={payment.method} onValueChange={(val: any) => setPayment(prev => ({ ...prev, method: val }))}><SelectTrigger className="h-8 text-sm mt-1"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="cash">Готівка</SelectItem><SelectItem value="card">Картка</SelectItem><SelectItem value="bank_transfer">Банківський переказ</SelectItem><SelectItem value="credit">В кредит</SelectItem><SelectItem value="installment">Розстрочка</SelectItem></SelectContent></Select></div>
                      <div><Label className="text-xs text-slate-500">Оплатити до</Label><Input type="date" value={payment.dueDate} onChange={(e) => setPayment(prev => ({ ...prev, dueDate: e.target.value }))} className="h-8 text-sm mt-1" /></div>
                      <div><Label className="text-xs text-slate-500">Статус оплати</Label><div className="mt-2">{remainingAmount <= 0 ? <Badge className="bg-emerald-100 text-emerald-600"><Check className="w-3 h-3 mr-1" /> Оплачено повністю</Badge> : paidAmount > 0 ? <Badge className="bg-amber-100 text-amber-600"><Clock className="w-3 h-3 mr-1" /> Частково оплачено</Badge> : <Badge className="bg-rose-100 text-rose-600"><AlertTriangle className="w-3 h-3 mr-1" /> Не оплачено</Badge>}</div></div>
                    </div>
                    {payment.method === 'installment' && <div><Label className="text-xs text-slate-500">Кількість місяців</Label><Select value={payment.installmentMonths?.toString()} onValueChange={(val) => setPayment(prev => ({ ...prev, installmentMonths: parseInt(val) }))}><SelectTrigger className="h-8 text-sm mt-1 w-40"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="3">3 місяці</SelectItem><SelectItem value="6">6 місяців</SelectItem><SelectItem value="12">12 місяців</SelectItem><SelectItem value="24">24 місяці</SelectItem></SelectContent></Select>{payment.installmentMonths && <p className="text-xs text-slate-500 mt-1">Щомісячний платіж: {Math.round((totalAmount + delivery.cost) / payment.installmentMonths).toLocaleString()} ₴</p>}</div>}
                    <div className="p-3 bg-slate-50 rounded-lg space-y-2">
                      <div className="flex justify-between text-sm"><span className="text-slate-500">Сума замовлення:</span><span className="font-medium">{totalAmount.toLocaleString()} ₴</span></div>
                      <div className="flex justify-between text-sm"><span className="text-slate-500">Доставка:</span><span className="font-medium">{delivery.cost.toLocaleString()} ₴</span></div>
                      <Separator />
                      <div className="flex justify-between text-sm font-medium"><span className="text-slate-500">Всього до оплати:</span><span>{(totalAmount + delivery.cost).toLocaleString()} ₴</span></div>
                      <Separator />
                      <div className="flex justify-between text-sm"><span className="text-slate-500">Сплачено:</span><span className="font-medium text-emerald-600">{paidAmount.toLocaleString()} ₴</span></div>
                      <div className="flex justify-between text-sm"><span className="text-slate-500">Залишок:</span><span className={cn("font-medium", remainingAmount > 0 ? "text-rose-600" : "text-emerald-600")}>{remainingAmount.toLocaleString()} ₴</span></div>
                    </div>
                    {payment.payments.length > 0 && <div><Label className="text-xs text-slate-500 mb-2">Історія платежів</Label><Table><TableHeader><TableRow className="h-8 bg-slate-50"><TableHead className="text-xs">Дата</TableHead><TableHead className="text-xs">Спосіб</TableHead><TableHead className="text-xs text-right">Сума</TableHead><TableHead className="text-xs text-center">Статус</TableHead></TableRow></TableHeader><TableBody>{payment.payments.map((pay) => (<TableRow key={pay.id} className="h-9"><TableCell className="text-xs">{pay.date}</TableCell><TableCell className="text-xs">{pay.method}</TableCell><TableCell className="text-xs text-right font-medium">{pay.amount.toLocaleString()} ₴</TableCell><TableCell className="text-center"><Badge className={cn('text-[10px]', pay.status === 'completed' ? 'bg-emerald-100 text-emerald-600' : pay.status === 'pending' ? 'bg-amber-100 text-amber-600' : 'bg-rose-100 text-rose-600')}>{pay.status === 'completed' ? 'Виконано' : pay.status === 'pending' ? 'Очікує' : 'Скасовано'}</Badge></TableCell></TableRow>))}</TableBody></Table></div>}
                    {remainingAmount > 0 && <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}><DialogTrigger asChild><Button variant="outline" size="sm" className="w-full"><Plus className="w-4 h-4 mr-2" /> Додати платіж</Button></DialogTrigger><DialogContent><DialogHeader><DialogTitle>Додати платіж</DialogTitle><DialogDescription>Залишок до оплати: {remainingAmount.toLocaleString()} ₴</DialogDescription></DialogHeader><div className="space-y-4 py-4"><div><Label>Сума платежу</Label><Input type="number" value={newPaymentAmount} onChange={(e) => setNewPaymentAmount(e.target.value)} placeholder="Введіть суму" max={remainingAmount} /></div><div className="flex justify-end gap-2"><Button variant="outline" onClick={() => setShowPaymentDialog(false)}>Скасувати</Button><Button onClick={handleAddPayment} className="bg-indigo-600">Додати платіж</Button></div></div></DialogContent></Dialog>}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Production Tab */}
              <TabsContent value="production" className="mt-4 space-y-4">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3"><div className="flex items-center justify-between"><CardTitle className="text-sm flex items-center gap-2"><Factory className="w-4 h-4" /> Виробничі завдання</CardTitle>{needsProduction && productionTasks.length === 0 && <Button size="sm" className="h-7 text-xs bg-indigo-600 hover:bg-indigo-700" onClick={handleCreateProductionTasks}><Plus className="w-3.5 h-3.5 mr-1" /> Створити завдання</Button>}</div></CardHeader>
                  <CardContent>
                    {needsProduction ? (
                      <div className="space-y-4">
                        <div className="flex items-center gap-4 p-3 bg-amber-50 rounded-lg"><Clock className="w-5 h-5 text-amber-600" /><div><p className="text-sm font-medium text-amber-800">Термін виробництва: {productionDays} робочих днів</p><p className="text-xs text-amber-600">Рекомендована дата відвантаження: {new Date(Date.now() + productionDays * 86400000).toLocaleDateString('uk-UA')}</p></div></div>
                        {productionTasks.length > 0 ? (
                          <Table>
                            <TableHeader><TableRow className="h-8 bg-slate-50"><TableHead className="text-xs">Товар</TableHead><TableHead className="text-xs text-center">К-ть</TableHead><TableHead className="text-xs">Термін</TableHead><TableHead className="text-xs">Робочий центр</TableHead><TableHead className="text-xs text-center">Статус</TableHead><TableHead className="text-xs text-center">Матеріали</TableHead><TableHead className="text-xs"></TableHead></TableRow></TableHeader>
                            <TableBody>
                              {productionTasks.map(task => (
                                <TableRow key={task.id} className="h-10">
                                  <TableCell><p className="text-sm font-medium">{task.productName}</p></TableCell>
                                  <TableCell className="text-center">{task.quantity}</TableCell>
                                  <TableCell>{task.deadline}</TableCell>
                                  <TableCell><Select value={task.workCenter} onValueChange={(val) => { setProductionTasks(prev => prev.map(t => t.id === task.id ? { ...t, workCenter: val } : t)); }}><SelectTrigger className="h-7 text-xs w-32"><SelectValue /></SelectTrigger><SelectContent>{workCenters.map(wc => <SelectItem key={wc.id} value={wc.name}>{wc.name}</SelectItem>)}</SelectContent></Select></TableCell>
                                  <TableCell className="text-center"><Select value={task.status} onValueChange={(val: any) => { setProductionTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: val } : t)); addHistoryRecord('Змінено статус виробництва', `${task.productName}: ${val}`); }}><SelectTrigger className="h-7 text-xs w-28"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="pending">Очікує</SelectItem><SelectItem value="planned">Заплановано</SelectItem><SelectItem value="in_progress">В роботі</SelectItem><SelectItem value="completed">Виконано</SelectItem></SelectContent></Select></TableCell>
                                  <TableCell className="text-center"><Checkbox checked={task.materialsReserved} onCheckedChange={(checked) => { setProductionTasks(prev => prev.map(t => t.id === task.id ? { ...t, materialsReserved: checked as boolean } : t)); if (checked) toast.success(`Матеріали для "${task.productName}" зарезервовано`); }} /></TableCell>
                                  <TableCell><DropdownMenu><DropdownMenuTrigger asChild><Button variant="ghost" size="icon" className="h-7 w-7"><MoreHorizontal className="w-4 h-4" /></Button></DropdownMenuTrigger><DropdownMenuContent align="end"><DropdownMenuItem onClick={() => toast.info('Призначити виконавця')}><User className="w-4 h-4 mr-2" /> Призначити виконавця</DropdownMenuItem><DropdownMenuItem onClick={() => toast.info('Деталі виробництва')}><Eye className="w-4 h-4 mr-2" /> Деталі</DropdownMenuItem></DropdownMenuContent></DropdownMenu></TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        ) : <div className="text-center py-6"><Factory className="w-10 h-10 text-slate-200 mx-auto mb-2" /><p className="text-sm text-slate-500">Виробничі завдання ще не створені</p><Button size="sm" className="mt-2 bg-indigo-600" onClick={handleCreateProductionTasks}><Plus className="w-4 h-4 mr-1" /> Створити завдання</Button></div>}
                      </div>
                    ) : <div className="text-center py-8"><CheckCircle2 className="w-12 h-12 text-emerald-200 mx-auto mb-2" /><p className="text-sm text-slate-500">Всі товари в наявності на складі</p><p className="text-xs text-slate-400">Виробництво не потрібно</p></div>}
                  </CardContent>
                </Card>
              </TabsContent>


              {/* Documents Tab */}
              <TabsContent value="documents" className="mt-4 space-y-4">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3"><div className="flex items-center justify-between"><CardTitle className="text-sm flex items-center gap-2"><FileText className="w-4 h-4" /> Пов'язані документи</CardTitle><div className="flex gap-2"><Button variant="outline" size="sm" className="h-7 text-xs" onClick={handleCreateInvoice}><Receipt className="w-3.5 h-3.5 mr-1" /> Рахунок</Button><Button variant="outline" size="sm" className="h-7 text-xs" onClick={handleCreateWaybill}><Truck className="w-3.5 h-3.5 mr-1" /> Накладна</Button></div></div></CardHeader>
                  <CardContent>
                    {documents.length > 0 ? (
                      <div className="space-y-2">
                        {documents.map(doc => (
                          <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-50">
                            <div className="flex items-center gap-3">
                              {doc.type === 'invoice' && <Receipt className="w-8 h-8 text-emerald-500" />}
                              {doc.type === 'waybill' && <Truck className="w-8 h-8 text-amber-500" />}
                              {doc.type === 'production_order' && <Factory className="w-8 h-8 text-indigo-500" />}
                              {doc.type === 'power_of_attorney' && <FileText className="w-8 h-8 text-blue-500" />}
                              {doc.type === 'contract' && <FileText className="w-8 h-8 text-slate-500" />}
                              <div>
                                <p className="text-sm font-medium">{doc.type === 'invoice' ? 'Рахунок на оплату' : doc.type === 'waybill' ? 'Накладна на відвантаження' : doc.type === 'production_order' ? 'Виробниче завдання' : doc.type === 'power_of_attorney' ? 'Довіреність' : 'Договір'}</p>
                                <p className="text-xs text-slate-400">№ {doc.number} від {doc.date}</p>
                                {doc.amount && <p className="text-xs text-slate-500">{doc.amount.toLocaleString()} ₴</p>}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Badge className={cn('text-[10px]', doc.status === 'paid' ? 'bg-emerald-100 text-emerald-600' : doc.status === 'issued' ? 'bg-blue-100 text-blue-600' : doc.status === 'sent' ? 'bg-amber-100 text-amber-600' : 'bg-slate-100 text-slate-600')}>{doc.status === 'draft' ? 'Чернетка' : doc.status === 'issued' ? 'Виписано' : doc.status === 'sent' ? 'Надіслано' : 'Оплачено'}</Badge>
                              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => toast.info('Перегляд документа')}><Eye className="w-4 h-4" /></Button>
                              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handlePrint(doc.type)}><Printer className="w-4 h-4" /></Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : <div className="text-center py-8"><FileText className="w-12 h-12 text-slate-200 mx-auto mb-2" /><p className="text-sm text-slate-500">Документи ще не створені</p><div className="flex justify-center gap-2 mt-3"><Button size="sm" variant="outline" onClick={handleCreateInvoice}><Receipt className="w-4 h-4 mr-1" /> Рахунок</Button><Button size="sm" variant="outline" onClick={handleCreateWaybill}><Truck className="w-4 h-4 mr-1" /> Накладна</Button></div></div>}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* History Tab */}
              <TabsContent value="history" className="mt-4 space-y-4">
                <Card className="shadow-sm">
                  <CardHeader className="pb-3"><CardTitle className="text-sm flex items-center gap-2"><History className="w-4 h-4" /> Історія змін</CardTitle></CardHeader>
                  <CardContent>
                    {history.length > 0 ? (
                      <div className="space-y-3">
                        {history.map((record, idx) => (
                          <div key={record.id} className={cn("flex items-start gap-3 p-3 border-l-2", idx === 0 ? "border-indigo-500 bg-indigo-50/50" : "border-slate-300 bg-slate-50")}>
                            <div className={cn("w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0", record.action.includes('створено') ? 'bg-emerald-100' : record.action.includes('проведено') ? 'bg-blue-100' : record.action.includes('видалено') ? 'bg-rose-100' : 'bg-slate-100')}>
                              {record.action.includes('створено') && <Plus className="w-4 h-4 text-emerald-600" />}
                              {record.action.includes('проведено') && <Check className="w-4 h-4 text-blue-600" />}
                              {record.action.includes('видалено') && <Trash2 className="w-4 h-4 text-rose-600" />}
                              {!['створено', 'проведено', 'видалено'].some(s => record.action.includes(s)) && <Edit3 className="w-4 h-4 text-slate-600" />}
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-medium">{record.action}</p>
                              {record.details && <p className="text-xs text-slate-500">{record.details}</p>}
                              {record.oldValue && record.newValue && <p className="text-xs text-slate-500">{record.oldValue} → {record.newValue}</p>}
                              <div className="flex items-center gap-2 mt-1"><span className="text-[10px] text-slate-400">{new Date(record.date).toLocaleString('uk-UA')}</span><span className="text-[10px] text-slate-400">•</span><span className="text-[10px] text-slate-400">{record.user}</span></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : <div className="text-center py-8"><History className="w-12 h-12 text-slate-200 mx-auto mb-2" /><p className="text-sm text-slate-500">Історія порожня</p><p className="text-xs text-slate-400">Зміни будуть відображатися тут</p></div>}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 bg-white border-l overflow-auto">
          <div className="p-4 space-y-4">
            {/* AI Insights */}
            {aiRecommendations.length > 0 && (
              <Card className="shadow-sm border-indigo-200 bg-gradient-to-br from-indigo-50 to-white">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Sparkles className="w-4 h-4 text-indigo-600" /> AI Рекомендації</CardTitle></CardHeader>
                <CardContent className="space-y-2">
                  {aiRecommendations.map((rec, idx) => (
                    <div key={idx} className={cn("p-2 rounded text-xs", rec.severity === 'warning' && "bg-amber-50 border border-amber-200", rec.severity === 'success' && "bg-emerald-50 border border-emerald-200", rec.severity === 'info' && "bg-blue-50 border border-blue-200")}>
                      <div className="flex items-start gap-1.5">
                        {rec.severity === 'warning' && <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" />}
                        {rec.severity === 'success' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />}
                        {rec.severity === 'info' && <Zap className="w-3.5 h-3.5 text-blue-500 flex-shrink-0 mt-0.5" />}
                        <div className="flex-1">
                          <p className={cn(rec.severity === 'warning' && "text-amber-800", rec.severity === 'success' && "text-emerald-800", rec.severity === 'info' && "text-blue-800")}>{rec.message}</p>
                          {rec.action && <Button variant="link" size="sm" className="h-auto p-0 text-[10px] mt-1" onClick={() => { if (rec.action?.includes('виробництво')) { setActiveTab('production'); handleCreateProductionTasks(); } }}>{rec.action}</Button>}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Order Summary */}
            <Card className="shadow-sm">
              <CardHeader className="pb-2"><CardTitle className="text-sm">Підсумки замовлення</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-slate-500">Кількість товарів:</span><span>{items.reduce((sum, i) => sum + i.quantity, 0)} шт</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Всього позицій:</span><span>{items.length}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Знижка:</span><span className="text-rose-600">-{discountTotal.toLocaleString()} ₴</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Доставка:</span><span>{delivery.cost.toLocaleString()} ₴</span></div>
                  <Separator />
                  <div className="flex justify-between"><span className="text-slate-500">Сума без ПДВ:</span><span>{(subtotal - vatTotal).toLocaleString()} ₴</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">ПДВ (20%):</span><span>{vatTotal.toLocaleString()} ₴</span></div>
                  <Separator />
                  <div className="flex justify-between text-base font-semibold"><span>ВСЬОГО:</span><span className="text-indigo-600">{(totalAmount + delivery.cost).toLocaleString()} ₴</span></div>
                </div>
                {selectedCustomer && selectedCustomer.discount > 0 && <div className="p-2 bg-emerald-50 rounded text-xs text-emerald-700"><Check className="w-3.5 h-3.5 inline mr-1" /> Знижка клієнта {selectedCustomer.discount}% застосована</div>}
                {paidAmount > 0 && <div className="p-2 bg-slate-50 rounded text-xs"><div className="flex justify-between"><span className="text-slate-500">Сплачено:</span><span className="text-emerald-600 font-medium">{paidAmount.toLocaleString()} ₴</span></div><div className="flex justify-between mt-1"><span className="text-slate-500">Залишок:</span><span className={remainingAmount > 0 ? "text-rose-600" : "text-emerald-600"}>{remainingAmount.toLocaleString()} ₴</span></div></div>}
              </CardContent>
            </Card>

            {/* Profit Analysis */}
            {items.length > 0 && (
              <Card className="shadow-sm">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><BarChart3 className="w-4 h-4" /> Аналіз прибутку</CardTitle></CardHeader>
                <CardContent className="space-y-2">
                  {(() => {
                    const totalCost = items.reduce((sum, item) => sum + (item.costPrice * item.quantity), 0);
                    const profit = totalAmount - totalCost;
                    const margin = totalAmount > 0 ? (profit / totalAmount) * 100 : 0;
                    return (
                      <>
                        <div className="flex justify-between text-sm"><span className="text-slate-500">Собівартість:</span><span>{totalCost.toLocaleString()} ₴</span></div>
                        <div className="flex justify-between text-sm"><span className="text-slate-500">Прибуток:</span><span className={cn("font-medium", profit > 0 ? "text-emerald-600" : "text-rose-600")}>{profit.toLocaleString()} ₴</span></div>
                        <div className="flex justify-between text-sm"><span className="text-slate-500">Маржа:</span><Badge className={cn('text-[10px]', margin >= 30 ? 'bg-emerald-100 text-emerald-600' : margin >= 20 ? 'bg-amber-100 text-amber-600' : 'bg-rose-100 text-rose-600')}>{margin.toFixed(1)}%</Badge></div>
                        <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden"><div className={cn("h-full rounded-full", margin >= 30 ? 'bg-emerald-500' : margin >= 20 ? 'bg-amber-500' : 'bg-rose-500')} style={{ width: `${Math.min(margin, 100)}%` }} /></div>
                      </>
                    );
                  })()}
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Card className="shadow-sm">
              <CardHeader className="pb-2"><CardTitle className="text-sm">Швидкі дії</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" size="sm" className="w-full h-8 text-xs justify-start" onClick={() => toast.info('Калькуляція замовлення')}><Calculator className="w-3.5 h-3.5 mr-2" /> Калькуляція замовлення</Button>
                <Button variant="outline" size="sm" className="w-full h-8 text-xs justify-start" onClick={() => toast.info('Договір з клієнтом')}><FileText className="w-3.5 h-3.5 mr-2" /> Договір з клієнтом</Button>
                <Button variant="outline" size="sm" className="w-full h-8 text-xs justify-start" onClick={handleSendEmail} disabled={!selectedCustomer?.email}><Send className="w-3.5 h-3.5 mr-2" /> Надіслати пропозицію</Button>
                {needsProduction && productionTasks.length === 0 && <Button size="sm" className="w-full h-8 text-xs justify-start bg-amber-600 hover:bg-amber-700" onClick={() => { setActiveTab('production'); handleCreateProductionTasks(); }}><Factory className="w-3.5 h-3.5 mr-2" /> Запустити в виробництво</Button>}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Print Dialog */}
      <Dialog open={showPrintDialog} onOpenChange={setShowPrintDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Друк документа</DialogTitle></DialogHeader>
          <div className="space-y-2 py-4">
            <Button variant="outline" className="w-full justify-start" onClick={() => handlePrint('order')}><FileText className="w-4 h-4 mr-2" /> Замовлення покупця</Button>
            <Button variant="outline" className="w-full justify-start" onClick={() => handlePrint('invoice')}><Receipt className="w-4 h-4 mr-2" /> Рахунок на оплату</Button>
            <Button variant="outline" className="w-full justify-start" onClick={() => handlePrint('waybill')}><Truck className="w-4 h-4 mr-2" /> Накладна</Button>
            <Button variant="outline" className="w-full justify-start" onClick={() => handlePrint('specification')}><Package className="w-4 h-4 mr-2" /> Специфікація</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
