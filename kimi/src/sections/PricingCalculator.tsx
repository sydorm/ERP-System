import { useState } from 'react';
import { 
  ArrowLeft, 
  Save, 
  Calculator, 
  Users, 
  Clock, 
  TrendingUp,
  Package,
  CheckCircle2,
  Wrench
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

// Типи оплати праці
interface PaymentType {
  id: string;
  name: string;
  type: 'hourly' | 'piecework' | 'salary';
  rate: number;
  unit: string;
}

// Робочі операції
interface Operation {
  id: string;
  name: string;
  department: string;
  timeMinutes: number;
  paymentType: string;
  laborCost: number;
}

// Співробітники
// interface Employee {
//   id: string;
//   name: string;
//   position: string;
//   hourlyRate: number;
//   department: string;
// }

const paymentTypes: PaymentType[] = [
  { id: 'hourly_basic', name: 'Погодинна (основна)', type: 'hourly', rate: 85, unit: '₴/год' },
  { id: 'hourly_premium', name: 'Погодинна (преміальна)', type: 'hourly', rate: 120, unit: '₴/год' },
  { id: 'piecework', name: 'Відрядна', type: 'piecework', rate: 45, unit: '₴/шт' },
  { id: 'salary', name: 'Оклад (місячний)', type: 'salary', rate: 15000, unit: '₴/міс' },
];

const operations: Operation[] = [
  { id: '1', name: 'Розкрій металу', department: 'Розкрійний цех', timeMinutes: 15, paymentType: 'hourly_basic', laborCost: 21.25 },
  { id: '2', name: 'Гнуття металу', department: 'Гнуття', timeMinutes: 20, paymentType: 'hourly_basic', laborCost: 28.33 },
  { id: '3', name: 'Зварювання', department: 'Зварювальний цех', timeMinutes: 30, paymentType: 'hourly_premium', laborCost: 60.00 },
  { id: '4', name: 'Шліфування', department: 'Обробка', timeMinutes: 25, paymentType: 'hourly_basic', laborCost: 35.42 },
  { id: '5', name: 'Фарбування', department: 'Фарбувальний цех', timeMinutes: 40, paymentType: 'hourly_premium', laborCost: 80.00 },
  { id: '6', name: 'Збірка', department: 'Збірка', timeMinutes: 35, paymentType: 'piecework', laborCost: 45.00 },
  { id: '7', name: 'Упаковка', department: 'Упаковка', timeMinutes: 10, paymentType: 'hourly_basic', laborCost: 14.17 },
];

/* const employees: Employee[] = [
  { id: '1', name: 'Іванов П.', position: 'Різальник', hourlyRate: 85, department: 'Розкрійний цех' },
  { id: '2', name: 'Петров С.', position: 'Гнутик', hourlyRate: 90, department: 'Гнуття' },
  { id: '3', name: 'Сидоров М.', position: 'Зварювальник', hourlyRate: 120, department: 'Зварювальний цех' },
  { id: '4', name: 'Коваленко А.', position: 'Шліфувальник', hourlyRate: 85, department: 'Обробка' },
  { id: '5', name: 'Мельник О.', position: 'Маляр', hourlyRate: 120, department: 'Фарбувальний цех' },
  { id: '6', name: 'Шевченко І.', position: 'Збиральник', hourlyRate: 95, department: 'Збірка' },
]; */

// Дані BOM для розрахунку
interface BOMItem {
  name: string;
  amount: number;
  unit: string;
  pricePerUnit: number;
  totalPrice: number;
}

const bomItems: BOMItem[] = [
  { name: 'Сталь листова 2мм', amount: 2.5, unit: 'кг', pricePerUnit: 45, totalPrice: 112.5 },
  { name: 'Клей столярний', amount: 0.5, unit: 'кг', pricePerUnit: 120, totalPrice: 60 },
  { name: 'Фарба порошкова', amount: 0.3, unit: 'кг', pricePerUnit: 180, totalPrice: 54 },
];

export function PricingCalculator({ onBack, onSave }: { onBack: () => void; onSave: () => void }) {
  const [selectedOperations, setSelectedOperations] = useState<string[]>(['1', '2', '3', '6']);
  const [overheadPercent, setOverheadPercent] = useState(25);
  const [profitPercent, setProfitPercent] = useState(30);
  const [vatPercent, setVatPercent] = useState(20);
  const [includeOverhead, setIncludeOverhead] = useState(true);
  const [includeProfit, setIncludeProfit] = useState(true);
  const [includeVAT, setIncludeVAT] = useState(true);

  // Розрахунки
  const materialsCost = bomItems.reduce((sum, item) => sum + item.totalPrice, 0);
  
  const laborCost = selectedOperations.reduce((sum, opId) => {
    const op = operations.find(o => o.id === opId);
    return sum + (op?.laborCost || 0);
  }, 0);

  const totalTime = selectedOperations.reduce((sum, opId) => {
    const op = operations.find(o => o.id === opId);
    return sum + (op?.timeMinutes || 0);
  }, 0);

  const overheadCost = includeOverhead ? (materialsCost + laborCost) * (overheadPercent / 100) : 0;
  const productionCost = materialsCost + laborCost + overheadCost;
  const profitAmount = includeProfit ? productionCost * (profitPercent / 100) : 0;
  const wholesalePrice = productionCost + profitAmount;
  const vatAmount = includeVAT ? wholesalePrice * (vatPercent / 100) : 0;
  const retailPrice = wholesalePrice + vatAmount;

  const handleToggleOperation = (opId: string) => {
    setSelectedOperations(prev => 
      prev.includes(opId) 
        ? prev.filter(id => id !== opId)
        : [...prev, opId]
    );
  };

  const handleSave = () => {
    toast.success('Ціноутворення збережено');
    onSave();
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
            <h2 className="text-lg font-bold text-slate-900">Розумне ціноутворення</h2>
            <p className="text-xs text-slate-500">Розрахунок собівартості та цін продажу</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onBack}>
            Скасувати
          </Button>
          <Button size="sm" onClick={handleSave} className="bg-indigo-600 hover:bg-indigo-700">
            <Save className="w-3.5 h-3.5 mr-1.5" />
            Зберегти
          </Button>
        </div>
      </div>

      <Tabs defaultValue="calculator" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calculator" className="text-xs">
            <Calculator className="w-3.5 h-3.5 mr-1.5" />
            Калькулятор цін
          </TabsTrigger>
          <TabsTrigger value="operations" className="text-xs">
            <Wrench className="w-3.5 h-3.5 mr-1.5" />
            Операції
          </TabsTrigger>
          <TabsTrigger value="history" className="text-xs">
            <TrendingUp className="w-3.5 h-3.5 mr-1.5" />
            Історія цін
          </TabsTrigger>
        </TabsList>

        <TabsContent value="calculator" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Panel - Cost Components */}
            <div className="lg:col-span-2 space-y-4">
              {/* Materials Cost */}
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Package className="w-4 h-4" />
                    Вартість матеріалів (з BOM)
                  </h3>
                  <Badge variant="secondary" className="text-[10px]">
                    {bomItems.length} позицій
                  </Badge>
                </div>
                <div className="space-y-2">
                  {bomItems.map((item, i) => (
                    <div key={i} className="flex justify-between text-sm py-1 border-b border-slate-100 last:border-0">
                      <span className="text-slate-600">{item.name}</span>
                      <span className="font-medium">{item.totalPrice.toFixed(2)} ₴</span>
                    </div>
                  ))}
                  <div className="flex justify-between pt-2 border-t">
                    <span className="text-sm font-medium">Разом матеріали:</span>
                    <span className="text-lg font-bold text-indigo-600">{materialsCost.toFixed(2)} ₴</span>
                  </div>
                </div>
              </Card>

              {/* Labor Cost */}
              <Card className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Вартість робочої сили
                  </h3>
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-xs text-slate-500">{Math.floor(totalTime / 60)}год {totalTime % 60}хв</span>
                  </div>
                </div>
                <div className="space-y-2">
                  {operations.filter(op => selectedOperations.includes(op.id)).map(op => (
                    <div key={op.id} className="flex justify-between items-center text-sm py-1 border-b border-slate-100 last:border-0">
                      <div>
                        <span className="text-slate-700">{op.name}</span>
                        <span className="text-[10px] text-slate-400 ml-2">({op.timeMinutes} хв)</span>
                      </div>
                      <span className="font-medium">{op.laborCost.toFixed(2)} ₴</span>
                    </div>
                  ))}
                  <div className="flex justify-between pt-2 border-t">
                    <span className="text-sm font-medium">Разом робота:</span>
                    <span className="text-lg font-bold text-emerald-600">{laborCost.toFixed(2)} ₴</span>
                  </div>
                </div>
              </Card>

              {/* Overhead & Settings */}
              <Card className="p-4">
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Накладні витрати та прибуток
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-xs">Накладні</Label>
                      <Switch 
                        checked={includeOverhead} 
                        onCheckedChange={setIncludeOverhead}
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <Input 
                        type="number" 
                        value={overheadPercent}
                        onChange={(e) => setOverheadPercent(Number(e.target.value))}
                        className="h-8 text-sm"
                        disabled={!includeOverhead}
                      />
                      <span className="text-sm text-slate-500">%</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      = {overheadCost.toFixed(2)} ₴
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-xs">Прибуток</Label>
                      <Switch 
                        checked={includeProfit} 
                        onCheckedChange={setIncludeProfit}
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <Input 
                        type="number" 
                        value={profitPercent}
                        onChange={(e) => setProfitPercent(Number(e.target.value))}
                        className="h-8 text-sm"
                        disabled={!includeProfit}
                      />
                      <span className="text-sm text-slate-500">%</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      = {profitAmount.toFixed(2)} ₴
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label className="text-xs">ПДВ</Label>
                      <Switch 
                        checked={includeVAT} 
                        onCheckedChange={setIncludeVAT}
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <Input 
                        type="number" 
                        value={vatPercent}
                        onChange={(e) => setVatPercent(Number(e.target.value))}
                        className="h-8 text-sm"
                        disabled={!includeVAT}
                      />
                      <span className="text-sm text-slate-500">%</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      = {vatAmount.toFixed(2)} ₴
                    </p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Right Panel - Price Summary */}
            <div className="space-y-4">
              <Card className="p-4 bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
                <h3 className="text-sm font-semibold mb-4 text-indigo-900">Розрахунок ціни</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Матеріали:</span>
                    <span className="font-medium">{materialsCost.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Робота:</span>
                    <span className="font-medium">{laborCost.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Накладні ({overheadPercent}%):</span>
                    <span className="font-medium">{overheadCost.toFixed(2)} ₴</span>
                  </div>
                  <div className="border-t border-indigo-200 pt-2">
                    <div className="flex justify-between text-sm font-medium">
                      <span className="text-indigo-900">Собівартість:</span>
                      <span className="text-indigo-900">{productionCost.toFixed(2)} ₴</span>
                    </div>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Прибуток ({profitPercent}%):</span>
                    <span className="font-medium text-emerald-600">+{profitAmount.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Оптова ціна:</span>
                    <span className="font-medium">{wholesalePrice.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">ПДВ ({vatPercent}%):</span>
                    <span className="font-medium">{vatAmount.toFixed(2)} ₴</span>
                  </div>
                  <div className="border-t-2 border-indigo-300 pt-3 mt-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-bold text-indigo-900">Роздрібна ціна:</span>
                      <span className="text-2xl font-bold text-indigo-600">{retailPrice.toFixed(2)} ₴</span>
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="text-sm font-semibold mb-3">Рентабельність</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Маржа:</span>
                    <span className="font-medium text-emerald-600">
                      {((profitAmount / wholesalePrice) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Націнка:</span>
                    <span className="font-medium text-emerald-600">
                      {((profitAmount / productionCost) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Виробничий час:</span>
                    <span className="font-medium">{Math.floor(totalTime / 60)}год {totalTime % 60}хв</span>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="text-sm font-semibold mb-3">Порівняння цін</h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Закупівельна:</span>
                    <span>{materialsCost.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Собівартість:</span>
                    <span>{productionCost.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Оптова:</span>
                    <span>{wholesalePrice.toFixed(2)} ₴</span>
                  </div>
                  <div className="flex justify-between font-medium">
                    <span className="text-slate-700">Роздрібна:</span>
                    <span className="text-indigo-600">{retailPrice.toFixed(2)} ₴</span>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="operations" className="space-y-4">
          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-4">Виберіть операції для виробу</h3>
            <div className="space-y-2">
              {operations.map(op => (
                <div 
                  key={op.id} 
                  className={cn(
                    'flex items-center justify-between p-3 rounded-lg border transition-all cursor-pointer',
                    selectedOperations.includes(op.id)
                      ? 'border-indigo-300 bg-indigo-50'
                      : 'border-slate-200 hover:border-slate-300'
                  )}
                  onClick={() => handleToggleOperation(op.id)}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      'w-5 h-5 rounded border flex items-center justify-center',
                      selectedOperations.includes(op.id)
                        ? 'bg-indigo-600 border-indigo-600'
                        : 'border-slate-300'
                    )}>
                      {selectedOperations.includes(op.id) && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{op.name}</p>
                      <p className="text-[10px] text-slate-500">{op.department}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{op.laborCost.toFixed(2)} ₴</p>
                    <p className="text-[10px] text-slate-500">{op.timeMinutes} хв</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-4">Типи оплати праці</h3>
            <div className="grid grid-cols-2 gap-3">
              {paymentTypes.map(pt => (
                <div key={pt.id} className="p-3 border rounded-lg">
                  <p className="text-sm font-medium">{pt.name}</p>
                  <p className="text-xs text-slate-500">{pt.rate} {pt.unit}</p>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-4">Історія змін цін</h3>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-50">
                  <tr className="h-9">
                    <th className="px-3 text-left text-xs font-medium text-slate-600">Дата</th>
                    <th className="px-3 text-left text-xs font-medium text-slate-600">Користувач</th>
                    <th className="px-3 text-right text-xs font-medium text-slate-600">Собівартість</th>
                    <th className="px-3 text-right text-xs font-medium text-slate-600">Оптова</th>
                    <th className="px-3 text-right text-xs font-medium text-slate-600">Роздрібна</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-t h-10">
                    <td className="px-3 text-sm">07.03.2026 14:30</td>
                    <td className="px-3 text-sm">Адміністратор</td>
                    <td className="px-3 text-sm text-right">{productionCost.toFixed(2)} ₴</td>
                    <td className="px-3 text-sm text-right">{wholesalePrice.toFixed(2)} ₴</td>
                    <td className="px-3 text-sm text-right font-medium">{retailPrice.toFixed(2)} ₴</td>
                  </tr>
                  <tr className="border-t h-10">
                    <td className="px-3 text-sm">05.03.2026 10:15</td>
                    <td className="px-3 text-sm">Менеджер</td>
                    <td className="px-3 text-sm text-right">385.50 ₴</td>
                    <td className="px-3 text-sm text-right">501.15 ₴</td>
                    <td className="px-3 text-sm text-right font-medium">601.38 ₴</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
