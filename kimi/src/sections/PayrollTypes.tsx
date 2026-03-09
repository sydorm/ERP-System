import { useState } from 'react';
import { 
  Plus, 
  Search, 
  TrendingUp,
  TrendingDown,
  Save
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
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
// import { cn } from '@/lib/utils';
import { toast } from 'sonner';

type PaymentType = 'addition' | 'deduction';
type CalculationMethod = 'fixed' | 'percentage' | 'per_hour' | 'per_piece';

interface PayrollType {
  id: string;
  name: string;
  code: string;
  type: PaymentType;
  calculationMethod: CalculationMethod;
  defaultValue: number;
  isTaxable: boolean;
  isActive: boolean;
  description?: string;
}

const initialTypes: PayrollType[] = [
  {
    id: '1',
    name: 'Основна зарплата',
    code: 'BASE_SALARY',
    type: 'addition',
    calculationMethod: 'per_hour',
    defaultValue: 85,
    isTaxable: true,
    isActive: true,
    description: 'Базова оплата за годину роботи',
  },
  {
    id: '2',
    name: 'Премія',
    code: 'BONUS',
    type: 'addition',
    calculationMethod: 'fixed',
    defaultValue: 1000,
    isTaxable: true,
    isActive: true,
    description: 'За високу продуктивність',
  },
  {
    id: '3',
    name: 'Овертайм',
    code: 'OVERTIME',
    type: 'addition',
    calculationMethod: 'per_hour',
    defaultValue: 127.5,
    isTaxable: true,
    isActive: true,
    description: 'Понаднормові години (1.5x)',
  },
  {
    id: '4',
    name: 'Відрядна оплата',
    code: 'PIECEWORK',
    type: 'addition',
    calculationMethod: 'per_piece',
    defaultValue: 45,
    isTaxable: true,
    isActive: true,
    description: 'Оплата за виріб',
  },
  {
    id: '5',
    name: 'Податок на доходи',
    code: 'INCOME_TAX',
    type: 'deduction',
    calculationMethod: 'percentage',
    defaultValue: 18,
    isTaxable: false,
    isActive: true,
    description: 'ПДФО 18%',
  },
  {
    id: '6',
    name: 'Військовий збір',
    code: 'MILITARY_TAX',
    type: 'deduction',
    calculationMethod: 'percentage',
    defaultValue: 1.5,
    isTaxable: false,
    isActive: true,
    description: 'Військовий збір 1.5%',
  },
  {
    id: '7',
    name: 'ЄСВ (роботодавець)',
    code: 'ESV',
    type: 'deduction',
    calculationMethod: 'percentage',
    defaultValue: 22,
    isTaxable: false,
    isActive: true,
    description: 'Єдиний соціальний внесок',
  },
  {
    id: '8',
    name: 'Штраф за запізнення',
    code: 'LATE_FINE',
    type: 'deduction',
    calculationMethod: 'fixed',
    defaultValue: 100,
    isTaxable: false,
    isActive: true,
    description: 'За запізнення на роботу',
  },
];

const methodLabels: Record<CalculationMethod, string> = {
  fixed: 'Фіксована сума',
  percentage: 'Відсоток',
  per_hour: 'За годину',
  per_piece: 'За виріб',
};

export function PayrollTypes() {
  const [types, setTypes] = useState<PayrollType[]>(initialTypes);
  const [searchQuery, setSearchQuery] = useState('');
  const [isNewTypeOpen, setIsNewTypeOpen] = useState(false);

  const filteredTypes = types.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const additions = filteredTypes.filter(t => t.type === 'addition');
  const deductions = filteredTypes.filter(t => t.type === 'deduction');

  const handleToggleActive = (id: string) => {
    setTypes(prev => prev.map(t => t.id === id ? { ...t, isActive: !t.isActive } : t));
  };

  return (
    <div className="space-y-3">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 bg-white p-3 rounded-lg shadow-sm">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input 
            placeholder="Пошук..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-8 text-sm"
          />
        </div>
        <Dialog open={isNewTypeOpen} onOpenChange={setIsNewTypeOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="h-8 text-xs bg-indigo-600 hover:bg-indigo-700 ml-auto">
              <Plus className="w-3.5 h-3.5 mr-1" />
              Новий вид
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-base">Новий вид нарахування</DialogTitle>
            </DialogHeader>
            <div className="space-y-3 py-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">Назва</Label>
                  <Input placeholder="Наприклад: Премія" className="h-9 text-sm" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Код</Label>
                  <Input placeholder="BONUS" className="h-9 text-sm" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">Тип</Label>
                  <Select defaultValue="addition">
                    <SelectTrigger className="h-9 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="addition">Нарахування (+)</SelectItem>
                      <SelectItem value="deduction">Утримання (-)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Метод розрахунку</Label>
                  <Select defaultValue="fixed">
                    <SelectTrigger className="h-9 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fixed">Фіксована сума</SelectItem>
                      <SelectItem value="percentage">Відсоток</SelectItem>
                      <SelectItem value="per_hour">За годину</SelectItem>
                      <SelectItem value="per_piece">За виріб</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Значення за замовчуванням</Label>
                <Input type="number" placeholder="0.00" className="h-9 text-sm" />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Опис</Label>
                <Input placeholder="Короткий опис..." className="h-9 text-sm" />
              </div>
              <div className="flex items-center justify-between p-2 bg-slate-50 rounded">
                <div>
                  <p className="text-sm font-medium">Обкладається податком</p>
                  <p className="text-xs text-slate-500">Враховується при розрахунку ПДФО</p>
                </div>
                <Switch defaultChecked />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsNewTypeOpen(false)}>
                Скасувати
              </Button>
              <Button 
                onClick={() => {
                  toast.success('Вид нарахування створено');
                  setIsNewTypeOpen(false);
                }}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <Save className="w-4 h-4 mr-2" />
                Зберегти
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Two Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Additions */}
        <Card className="overflow-hidden">
          <div className="p-3 border-b bg-emerald-50">
            <h3 className="text-sm font-semibold flex items-center gap-2 text-emerald-800">
              <TrendingUp className="w-4 h-4" />
              Нарахування (+)
            </h3>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="h-8">
                  <TableHead className="text-xs py-2">Назва</TableHead>
                  <TableHead className="text-xs py-2 text-center">Метод</TableHead>
                  <TableHead className="text-xs py-2 text-right">Значення</TableHead>
                  <TableHead className="text-xs py-2 text-center w-16">Акт.</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {additions.map((type) => (
                  <TableRow key={type.id} className="h-10 hover:bg-slate-50">
                    <TableCell className="py-2">
                      <div>
                        <p className="text-sm font-medium">{type.name}</p>
                        <p className="text-[10px] text-slate-400">{type.code}</p>
                      </div>
                    </TableCell>
                    <TableCell className="py-2 text-center">
                      <Badge variant="secondary" className="text-[10px]">
                        {methodLabels[type.calculationMethod]}
                      </Badge>
                    </TableCell>
                    <TableCell className="py-2 text-right">
                      <p className="text-sm font-medium">
                        {type.defaultValue}
                        {type.calculationMethod === 'percentage' && '%'}
                        {type.calculationMethod === 'per_hour' && ' ₴/год'}
                        {type.calculationMethod === 'per_piece' && ' ₴/шт'}
                        {type.calculationMethod === 'fixed' && ' ₴'}
                      </p>
                    </TableCell>
                    <TableCell className="py-2 text-center">
                      <Switch 
                        checked={type.isActive} 
                        onCheckedChange={() => handleToggleActive(type.id)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* Deductions */}
        <Card className="overflow-hidden">
          <div className="p-3 border-b bg-rose-50">
            <h3 className="text-sm font-semibold flex items-center gap-2 text-rose-800">
              <TrendingDown className="w-4 h-4" />
              Утримання (-)
            </h3>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="h-8">
                  <TableHead className="text-xs py-2">Назва</TableHead>
                  <TableHead className="text-xs py-2 text-center">Метод</TableHead>
                  <TableHead className="text-xs py-2 text-right">Значення</TableHead>
                  <TableHead className="text-xs py-2 text-center w-16">Акт.</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {deductions.map((type) => (
                  <TableRow key={type.id} className="h-10 hover:bg-slate-50">
                    <TableCell className="py-2">
                      <div>
                        <p className="text-sm font-medium">{type.name}</p>
                        <p className="text-[10px] text-slate-400">{type.code}</p>
                      </div>
                    </TableCell>
                    <TableCell className="py-2 text-center">
                      <Badge variant="secondary" className="text-[10px]">
                        {methodLabels[type.calculationMethod]}
                      </Badge>
                    </TableCell>
                    <TableCell className="py-2 text-right">
                      <p className="text-sm font-medium">
                        {type.defaultValue}
                        {type.calculationMethod === 'percentage' && '%'}
                        {type.calculationMethod === 'fixed' && ' ₴'}
                      </p>
                    </TableCell>
                    <TableCell className="py-2 text-center">
                      <Switch 
                        checked={type.isActive} 
                        onCheckedChange={() => handleToggleActive(type.id)}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      </div>

      {/* Info */}
      <Card className="p-4">
        <h4 className="text-sm font-semibold mb-2">Довідка</h4>
        <div className="grid grid-cols-2 gap-4 text-xs text-slate-600">
          <div>
            <p className="font-medium mb-1">Нарахування:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>Основна зарплата - базова оплата праці</li>
              <li>Премія - за додаткові досягнення</li>
              <li>Овертайм - понаднормові години</li>
              <li>Відрядна - оплата за кількість виробів</li>
            </ul>
          </div>
          <div>
            <p className="font-medium mb-1">Утримання:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>ПДФО - податок на доходи фізичних осіб (18%)</li>
              <li>Військовий збір - 1.5% від доходу</li>
              <li>ЄСВ - єдиний соціальний внесок (22%)</li>
              <li>Штрафи - за порушення трудової дисципліни</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
