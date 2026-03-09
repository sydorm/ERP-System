import { useState } from 'react';
import { 
  Calendar,
  DollarSign,
  CheckCircle2,
  Download,
  Calculator,
  Printer
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
// import {
//   Dialog,
//   DialogContent,
//   DialogHeader,
//   DialogTitle,
//   DialogFooter,
// } from '@/components/ui/dialog';
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

interface PayrollRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  position: string;
  department: string;
  period: string;
  paymentType: 'hourly' | 'salary' | 'piecework';
  hoursWorked: number;
  hourlyRate: number;
  piecesCompleted?: number;
  pieceRate?: number;
  baseSalary: number;
  bonus: number;
  overtime: number;
  deductions: number;
  tax: number;
  netSalary: number;
  status: 'draft' | 'calculated' | 'approved' | 'paid';
}

const initialPayroll: PayrollRecord[] = [
  {
    id: '1',
    employeeId: '1',
    employeeName: 'Іванов Петро Сергійович',
    position: 'Різальник',
    department: 'Розкрійний цех',
    period: '2024-03',
    paymentType: 'hourly',
    hoursWorked: 168,
    hourlyRate: 85,
    baseSalary: 14280,
    bonus: 1000,
    overtime: 0,
    deductions: 0,
    tax: 2570.40,
    netSalary: 12709.60,
    status: 'paid',
  },
  {
    id: '2',
    employeeId: '2',
    employeeName: 'Петров Сергій Михайлович',
    position: 'Гнутик',
    department: 'Гнуття',
    period: '2024-03',
    paymentType: 'hourly',
    hoursWorked: 160,
    hourlyRate: 90,
    baseSalary: 14400,
    bonus: 500,
    overtime: 1350,
    deductions: 0,
    tax: 2866.50,
    netSalary: 13383.50,
    status: 'approved',
  },
  {
    id: '3',
    employeeId: '3',
    employeeName: 'Сидоров Михайло Олегович',
    position: 'Зварювальник',
    department: 'Зварювальний цех',
    period: '2024-03',
    paymentType: 'hourly',
    hoursWorked: 172,
    hourlyRate: 120,
    baseSalary: 20640,
    bonus: 2000,
    overtime: 0,
    deductions: 0,
    tax: 4075.20,
    netSalary: 18564.80,
    status: 'calculated',
  },
  {
    id: '4',
    employeeId: '4',
    employeeName: 'Коваленко Анна Вікторівна',
    position: 'Менеджер',
    department: 'Офіс',
    period: '2024-03',
    paymentType: 'salary',
    hoursWorked: 168,
    hourlyRate: 0,
    baseSalary: 18000,
    bonus: 0,
    overtime: 0,
    deductions: 0,
    tax: 3240,
    netSalary: 14760,
    status: 'draft',
  },
];

const statusConfig = {
  draft: { label: 'Чернетка', color: 'bg-slate-100 text-slate-600' },
  calculated: { label: 'Розраховано', color: 'bg-blue-100 text-blue-600' },
  approved: { label: 'Затверджено', color: 'bg-amber-100 text-amber-600' },
  paid: { label: 'Виплачено', color: 'bg-emerald-100 text-emerald-600' },
};

export function Payroll() {
  const [payroll, setPayroll] = useState<PayrollRecord[]>(initialPayroll);
  const [selectedPeriod, setSelectedPeriod] = useState('2024-03');
  const [departmentFilter, setDepartmentFilter] = useState('all');

  const filteredPayroll = payroll.filter(p => 
    p.period === selectedPeriod && 
    (departmentFilter === 'all' || p.department === departmentFilter)
  );

  const stats = {
    totalEmployees: filteredPayroll.length,
    totalHours: filteredPayroll.reduce((s, p) => s + p.hoursWorked, 0),
    totalGross: filteredPayroll.reduce((s, p) => s + p.baseSalary + p.bonus + p.overtime, 0),
    totalNet: filteredPayroll.reduce((s, p) => s + p.netSalary, 0),
    totalTax: filteredPayroll.reduce((s, p) => s + p.tax, 0),
  };

  const handleCalculateAll = () => {
    toast.success('Зарплата розрахована для всіх співробітників');
    setPayroll(prev => prev.map(p => p.status === 'draft' ? { ...p, status: 'calculated' as const } : p));
  };

  const handleApproveAll = () => {
    toast.success('Зарплата затверджена');
    setPayroll(prev => prev.map(p => p.status === 'calculated' ? { ...p, status: 'approved' as const } : p));
  };

  return (
    <div className="space-y-3">
      {/* Stats */}
      <div className="grid grid-cols-5 gap-3">
        <Card className="p-3">
          <p className="text-[10px] text-slate-500 uppercase">Співробітників</p>
          <p className="text-xl font-bold text-slate-900">{stats.totalEmployees}</p>
        </Card>
        <Card className="p-3">
          <p className="text-[10px] text-slate-500 uppercase">Годин</p>
          <p className="text-xl font-bold text-blue-600">{stats.totalHours}</p>
        </Card>
        <Card className="p-3">
          <p className="text-[10px] text-slate-500 uppercase">Нараховано</p>
          <p className="text-xl font-bold text-indigo-600">{stats.totalGross.toLocaleString()} ₴</p>
        </Card>
        <Card className="p-3">
          <p className="text-[10px] text-slate-500 uppercase">Податки</p>
          <p className="text-xl font-bold text-rose-600">{stats.totalTax.toLocaleString()} ₴</p>
        </Card>
        <Card className="p-3">
          <p className="text-[10px] text-slate-500 uppercase">До виплати</p>
          <p className="text-xl font-bold text-emerald-600">{stats.totalNet.toLocaleString()} ₴</p>
        </Card>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 bg-white p-3 rounded-lg shadow-sm">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-400" />
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="h-8 text-sm w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2024-03">Березень 2024</SelectItem>
              <SelectItem value="2024-02">Лютий 2024</SelectItem>
              <SelectItem value="2024-01">Січень 2024</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
          <SelectTrigger className="h-8 text-sm w-36">
            <SelectValue placeholder="Відділ" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Всі відділи</SelectItem>
            <SelectItem value="Розкрійний цех">Розкрійний цех</SelectItem>
            <SelectItem value="Гнуття">Гнуття</SelectItem>
            <SelectItem value="Зварювальний цех">Зварювальний цех</SelectItem>
            <SelectItem value="Офіс">Офіс</SelectItem>
          </SelectContent>
        </Select>
        <div className="flex items-center gap-1 ml-auto">
          <Button variant="outline" size="sm" className="h-8 text-xs">
            <Download className="w-3.5 h-3.5 mr-1" />
            Експорт
          </Button>
          <Button variant="outline" size="sm" className="h-8 text-xs">
            <Printer className="w-3.5 h-3.5 mr-1" />
            Друк
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            className="h-8 text-xs"
            onClick={handleCalculateAll}
          >
            <Calculator className="w-3.5 h-3.5 mr-1" />
            Розрахувати
          </Button>
          <Button 
            size="sm" 
            className="h-8 text-xs bg-indigo-600 hover:bg-indigo-700"
            onClick={handleApproveAll}
          >
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
            Затвердити
          </Button>
        </div>
      </div>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50 h-9">
                <TableHead className="text-xs py-2">Співробітник</TableHead>
                <TableHead className="text-xs py-2 text-center">Годин</TableHead>
                <TableHead className="text-xs py-2 text-right">Ставка</TableHead>
                <TableHead className="text-xs py-2 text-right">Основна</TableHead>
                <TableHead className="text-xs py-2 text-right">Бонус</TableHead>
                <TableHead className="text-xs py-2 text-right">Податок</TableHead>
                <TableHead className="text-xs py-2 text-right">До виплати</TableHead>
                <TableHead className="text-xs py-2 text-center">Статус</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPayroll.map((record) => (
                <TableRow key={record.id} className="h-11 hover:bg-slate-50">
                  <TableCell className="py-2">
                    <div>
                      <p className="text-sm font-medium">{record.employeeName}</p>
                      <p className="text-[10px] text-slate-400">{record.position}</p>
                    </div>
                  </TableCell>
                  <TableCell className="py-2 text-center">
                    <p className="text-sm">{record.hoursWorked}</p>
                  </TableCell>
                  <TableCell className="py-2 text-right">
                    <p className="text-sm">{record.hourlyRate > 0 ? `${record.hourlyRate} ₴/год` : 'Оклад'}</p>
                  </TableCell>
                  <TableCell className="py-2 text-right">
                    <p className="text-sm">{record.baseSalary.toLocaleString()} ₴</p>
                  </TableCell>
                  <TableCell className="py-2 text-right">
                    <p className={cn('text-sm', record.bonus > 0 ? 'text-emerald-600' : 'text-slate-400')}>
                      {record.bonus > 0 ? `+${record.bonus.toLocaleString()}` : '0'} ₴
                    </p>
                  </TableCell>
                  <TableCell className="py-2 text-right">
                    <p className="text-sm text-rose-600">-{record.tax.toLocaleString()} ₴</p>
                  </TableCell>
                  <TableCell className="py-2 text-right">
                    <p className="text-sm font-bold text-emerald-600">{record.netSalary.toLocaleString()} ₴</p>
                  </TableCell>
                  <TableCell className="py-2 text-center">
                    <Badge className={cn('text-[10px]', statusConfig[record.status].color)}>
                      {statusConfig[record.status].label}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Summary */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <p className="text-xs text-slate-500">Всього нараховано</p>
              <p className="text-lg font-bold text-slate-900">{stats.totalGross.toLocaleString()} ₴</p>
            </div>
            <div className="text-2xl text-slate-300">-</div>
            <div>
              <p className="text-xs text-slate-500">Податки та збори</p>
              <p className="text-lg font-bold text-rose-600">{stats.totalTax.toLocaleString()} ₴</p>
            </div>
            <div className="text-2xl text-slate-300">=</div>
            <div>
              <p className="text-xs text-slate-500">До виплати</p>
              <p className="text-xl font-bold text-emerald-600">{stats.totalNet.toLocaleString()} ₴</p>
            </div>
          </div>
          <Button className="bg-emerald-600 hover:bg-emerald-700">
            <DollarSign className="w-4 h-4 mr-2" />
            Виплатити зарплату
          </Button>
        </div>
      </Card>
    </div>
  );
}
