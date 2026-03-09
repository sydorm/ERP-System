import { useState } from 'react';
import { 
  Plus, 
  Search, 
  Edit2,
  Trash2,
  User,
  Clock,
  DollarSign,
  CheckCircle2,
  Download
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
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
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

type EmployeeStatus = 'active' | 'inactive' | 'on_vacation' | 'sick_leave';

interface Employee {
  id: string;
  fullName: string;
  phone: string;
  email: string;
  position: string;
  department: string;
  hireDate: string;
  hourlyRate: number;
  salary?: number;
  status: EmployeeStatus;
  paymentType: 'hourly' | 'salary' | 'piecework';
}

const statusConfig: Record<EmployeeStatus, { label: string; color: string }> = {
  active: { label: 'Активний', color: 'bg-emerald-100 text-emerald-600' },
  inactive: { label: 'Неактивний', color: 'bg-slate-100 text-slate-600' },
  on_vacation: { label: 'Відпустка', color: 'bg-blue-100 text-blue-600' },
  sick_leave: { label: 'Лікарняний', color: 'bg-amber-100 text-amber-600' },
};

const departments = [
  'Розкрійний цех',
  'Гнуття',
  'Зварювальний цех',
  'Фарбувальний цех',
  'Деревообробка',
  'Збірка',
  'Упаковка',
  'Склад',
  'Офіс',
];

const positions = [
  'Різальник',
  'Гнутик',
  'Зварювальник',
  'Шліфувальник',
  'Маляр',
  'Столяр',
  'Збиральник',
  'Вантажник',
  'Менеджер',
  'Бухгалтер',
];

const initialEmployees: Employee[] = [
  {
    id: '1',
    fullName: 'Іванов Петро Сергійович',
    phone: '+380501234567',
    email: 'ivanov@company.com',
    position: 'Різальник',
    department: 'Розкрійний цех',
    hireDate: '2023-01-15',
    hourlyRate: 85,
    status: 'active',
    paymentType: 'hourly',
  },
  {
    id: '2',
    fullName: 'Петров Сергій Михайлович',
    phone: '+380671112233',
    email: 'petrov@company.com',
    position: 'Гнутик',
    department: 'Гнуття',
    hireDate: '2023-03-10',
    hourlyRate: 90,
    status: 'active',
    paymentType: 'hourly',
  },
  {
    id: '3',
    fullName: 'Сидоров Михайло Олегович',
    phone: '+380933334455',
    email: 'sidorov@company.com',
    position: 'Зварювальник',
    department: 'Зварювальний цех',
    hireDate: '2022-06-20',
    hourlyRate: 120,
    status: 'active',
    paymentType: 'hourly',
  },
  {
    id: '4',
    fullName: 'Коваленко Анна Вікторівна',
    phone: '+380504445566',
    email: 'kovalenko@company.com',
    position: 'Менеджер',
    department: 'Офіс',
    hireDate: '2023-09-01',
    hourlyRate: 0,
    salary: 18000,
    status: 'active',
    paymentType: 'salary',
  },
  {
    id: '5',
    fullName: 'Мельник Олег Іванович',
    phone: '+380955556677',
    email: 'melnyk@company.com',
    position: 'Маляр',
    department: 'Фарбувальний цех',
    hireDate: '2022-11-15',
    hourlyRate: 110,
    status: 'on_vacation',
    paymentType: 'hourly',
  },
  {
    id: '6',
    fullName: 'Шевченко Ірина Петрівна',
    phone: '+380966667788',
    email: 'shevchenko@company.com',
    position: 'Бухгалтер',
    department: 'Офіс',
    hireDate: '2021-05-10',
    hourlyRate: 0,
    salary: 22000,
    status: 'active',
    paymentType: 'salary',
  },
];

export function Employees() {
  const [employees, setEmployees] = useState<Employee[]>(initialEmployees);
  const [searchQuery, setSearchQuery] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState<string>('all');
  const [isNewEmployeeOpen, setIsNewEmployeeOpen] = useState(false);

  const filteredEmployees = employees.filter(emp => {
    const matchesSearch = 
      emp.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.phone.includes(searchQuery) ||
      emp.position.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = departmentFilter === 'all' || emp.department === departmentFilter;
    return matchesSearch && matchesDept;
  });

  const stats = {
    total: employees.length,
    active: employees.filter(e => e.status === 'active').length,
    hourly: employees.filter(e => e.paymentType === 'hourly').length,
    salary: employees.filter(e => e.paymentType === 'salary').length,
  };

  const handleDelete = (id: string) => {
    setEmployees(prev => prev.filter(e => e.id !== id));
    toast.success('Співробітника видалено');
  };

  return (
    <div className="space-y-3">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Всього</p>
              <p className="text-xl font-bold text-slate-900">{stats.total}</p>
            </div>
            <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center">
              <User className="w-4 h-4 text-slate-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Активні</p>
              <p className="text-xl font-bold text-emerald-600">{stats.active}</p>
            </div>
            <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Погодинні</p>
              <p className="text-xl font-bold text-blue-600">{stats.hourly}</p>
            </div>
            <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center">
              <Clock className="w-4 h-4 text-blue-600" />
            </div>
          </div>
        </Card>
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[10px] text-slate-500 uppercase">Окладники</p>
              <p className="text-xl font-bold text-indigo-600">{stats.salary}</p>
            </div>
            <div className="w-9 h-9 rounded-lg bg-indigo-100 flex items-center justify-center">
              <DollarSign className="w-4 h-4 text-indigo-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 bg-white p-3 rounded-lg shadow-sm">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input 
            placeholder="Пошук співробітників..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-8 text-sm"
          />
        </div>
        <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
          <SelectTrigger className="h-8 text-sm w-36">
            <SelectValue placeholder="Відділ" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Всі відділи</SelectItem>
            {departments.map(d => (
              <SelectItem key={d} value={d}>{d}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex items-center gap-1 ml-auto">
          <Button variant="outline" size="sm" className="h-8 text-xs">
            <Download className="w-3.5 h-3.5 mr-1" />
            Експорт
          </Button>
          <Dialog open={isNewEmployeeOpen} onOpenChange={setIsNewEmployeeOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-8 text-xs bg-indigo-600 hover:bg-indigo-700">
                <Plus className="w-3.5 h-3.5 mr-1" />
                Новий співробітник
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-base">Новий співробітник</DialogTitle>
              </DialogHeader>
              <div className="space-y-3 py-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">ПІБ</Label>
                    <Input placeholder="Прізвище Ім'я По батькові" className="h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Телефон</Label>
                    <Input placeholder="+380..." className="h-9 text-sm" />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Email</Label>
                  <Input type="email" placeholder="email@company.com" className="h-9 text-sm" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Відділ</Label>
                    <Select>
                      <SelectTrigger className="h-9 text-sm">
                        <SelectValue placeholder="Оберіть відділ" />
                      </SelectTrigger>
                      <SelectContent>
                        {departments.map(d => (
                          <SelectItem key={d} value={d}>{d}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Посада</Label>
                    <Select>
                      <SelectTrigger className="h-9 text-sm">
                        <SelectValue placeholder="Оберіть посаду" />
                      </SelectTrigger>
                      <SelectContent>
                        {positions.map(p => (
                          <SelectItem key={p} value={p}>{p}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Дата прийому</Label>
                    <Input type="date" className="h-9 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Тип оплати</Label>
                    <Select defaultValue="hourly">
                      <SelectTrigger className="h-9 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hourly">Погодинна</SelectItem>
                        <SelectItem value="salary">Оклад</SelectItem>
                        <SelectItem value="piecework">Відрядна</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Ставка / Оклад</Label>
                  <Input type="number" placeholder="0.00" className="h-9 text-sm" />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsNewEmployeeOpen(false)}>
                  Скасувати
                </Button>
                <Button 
                  onClick={() => {
                    toast.success('Співробітника додано');
                    setIsNewEmployeeOpen(false);
                  }}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  Зберегти
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50 h-9">
                <TableHead className="text-xs py-2">Співробітник</TableHead>
                <TableHead className="text-xs py-2">Посада</TableHead>
                <TableHead className="text-xs py-2 text-center">Статус</TableHead>
                <TableHead className="text-xs py-2 text-center">Тип оплати</TableHead>
                <TableHead className="text-xs py-2 text-right">Ставка</TableHead>
                <TableHead className="text-xs py-2 text-center w-20">Дії</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredEmployees.map((emp) => (
                <TableRow key={emp.id} className="h-11 hover:bg-slate-50">
                  <TableCell className="py-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 text-xs font-bold">
                        {emp.fullName.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{emp.fullName}</p>
                        <p className="text-[10px] text-slate-400">{emp.phone}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="py-2">
                    <div>
                      <p className="text-sm">{emp.position}</p>
                      <p className="text-[10px] text-slate-400">{emp.department}</p>
                    </div>
                  </TableCell>
                  <TableCell className="py-2 text-center">
                    <Badge className={cn('text-[10px]', statusConfig[emp.status].color)}>
                      {statusConfig[emp.status].label}
                    </Badge>
                  </TableCell>
                  <TableCell className="py-2 text-center">
                    <Badge variant="secondary" className="text-[10px]">
                      {emp.paymentType === 'hourly' && 'Погодинна'}
                      {emp.paymentType === 'salary' && 'Оклад'}
                      {emp.paymentType === 'piecework' && 'Відрядна'}
                    </Badge>
                  </TableCell>
                  <TableCell className="py-2 text-right">
                    <p className="text-sm font-medium">
                      {emp.paymentType === 'salary' 
                        ? `${emp.salary?.toLocaleString()} ₴/міс`
                        : `${emp.hourlyRate} ₴/год`
                      }
                    </p>
                  </TableCell>
                  <TableCell className="py-2">
                    <div className="flex items-center justify-center gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <Edit2 className="w-3.5 h-3.5 text-slate-400" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-7 w-7"
                        onClick={() => handleDelete(emp.id)}
                      >
                        <Trash2 className="w-3.5 h-3.5 text-rose-400" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}
