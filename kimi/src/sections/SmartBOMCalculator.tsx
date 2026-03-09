import { useState } from 'react';
import { 
  Calculator, 
  Plus, 
  Trash2, 
  Copy,
  Layers,
  Save,
  ArrowLeft,
  DollarSign,
  Info
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
} from '@/components/ui/dialog';
// import {
//   Accordion,
//   AccordionContent,
//   AccordionItem,
//   AccordionTrigger,
// } from '@/components/ui/accordion';
// import { cn } from '@/lib/utils';
import { toast } from 'sonner';

// Типи калькуляторів для різних матеріалів
interface CalculatorType {
  id: string;
  name: string;
  materialType: 'metal' | 'wood' | 'plastic' | 'glass' | 'fabric' | 'other';
  formula: string;
  parameters: {
    name: string;
    key: string;
    unit: string;
    defaultValue?: number;
  }[];
  wastePercent: number;
}

const calculatorTemplates: CalculatorType[] = [
  // Метал
  {
    id: 'metal_sheet',
    name: 'Листовий метал (площа)',
    materialType: 'metal',
    formula: '(length * width) / 1000000 * thickness * density',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Ширина', key: 'width', unit: 'мм' },
      { name: 'Товщина', key: 'thickness', unit: 'мм', defaultValue: 2 },
      { name: 'Щільність', key: 'density', unit: 'г/см³', defaultValue: 7.85 },
    ],
    wastePercent: 15,
  },
  {
    id: 'metal_tube',
    name: 'Металева труба (довжина)',
    materialType: 'metal',
    formula: 'length * weight_per_meter',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Вага погонного метра', key: 'weight_per_meter', unit: 'кг/м', defaultValue: 2.5 },
    ],
    wastePercent: 10,
  },
  {
    id: 'metal_rod',
    name: 'Металевий пруток',
    materialType: 'metal',
    formula: '(3.14159 * diameter * diameter / 4) * length * density / 1000000',
    parameters: [
      { name: 'Діаметр', key: 'diameter', unit: 'мм' },
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Щільність', key: 'density', unit: 'г/см³', defaultValue: 7.85 },
    ],
    wastePercent: 8,
  },
  // Дерево
  {
    id: 'wood_board',
    name: 'Дошка (обсяг)',
    materialType: 'wood',
    formula: '(length * width * thickness) / 1000000000',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Ширина', key: 'width', unit: 'мм' },
      { name: 'Товщина', key: 'thickness', unit: 'мм' },
    ],
    wastePercent: 20,
  },
  {
    id: 'wood_panel',
    name: 'Плита (площа)',
    materialType: 'wood',
    formula: '(length * width) / 1000000 * thickness / 1000',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Ширина', key: 'width', unit: 'мм' },
      { name: 'Товщина', key: 'thickness', unit: 'мм', defaultValue: 18 },
    ],
    wastePercent: 12,
  },
  // Пластик
  {
    id: 'plastic_sheet',
    name: 'Пластиковий лист',
    materialType: 'plastic',
    formula: '(length * width * thickness) / 1000000000 * density',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Ширина', key: 'width', unit: 'мм' },
      { name: 'Товщина', key: 'thickness', unit: 'мм' },
      { name: 'Щільність', key: 'density', unit: 'г/см³', defaultValue: 1.2 },
    ],
    wastePercent: 18,
  },
  // Скло
  {
    id: 'glass_sheet',
    name: 'Скло (площа)',
    materialType: 'glass',
    formula: '(length * width) / 1000000 * thickness / 1000 * 2500',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Ширина', key: 'width', unit: 'мм' },
      { name: 'Товщина', key: 'thickness', unit: 'мм', defaultValue: 4 },
    ],
    wastePercent: 25,
  },
  // Тканина
  {
    id: 'fabric',
    name: 'Тканина (площа)',
    materialType: 'fabric',
    formula: '(length * width) / 1000000',
    parameters: [
      { name: 'Довжина', key: 'length', unit: 'мм' },
      { name: 'Ширина', key: 'width', unit: 'мм' },
    ],
    wastePercent: 30,
  },
];

// Попередньо встановлені розміри для швидкого вибору
interface SizePreset {
  name: string;
  dimensions: Record<string, number>;
}

const sizePresets: Record<string, SizePreset[]> = {
  metal_sheet: [
    { name: 'Аналіз А (60×32×46)', dimensions: { length: 600, width: 320, thickness: 2 } },
    { name: 'Аналіз B (70×42×46)', dimensions: { length: 700, width: 420, thickness: 2 } },
    { name: 'Аналіз C (80×50×50)', dimensions: { length: 800, width: 500, thickness: 2 } },
    { name: 'Стандарт 1000×500', dimensions: { length: 1000, width: 500, thickness: 2 } },
  ],
  wood_board: [
    { name: 'Полиця 600×200', dimensions: { length: 600, width: 200, thickness: 18 } },
    { name: 'Полиця 800×250', dimensions: { length: 800, width: 250, thickness: 18 } },
    { name: 'Стілець 450×450', dimensions: { length: 450, width: 450, thickness: 25 } },
    { name: 'Стіл 1200×600', dimensions: { length: 1200, width: 600, thickness: 25 } },
  ],
};

interface BOMItem {
  id: string;
  materialId: string;
  materialName: string;
  calculatorType: string;
  parameters: Record<string, number>;
  calculatedAmount: number;
  unit: string;
  pricePerUnit: number;
  totalPrice: number;
  wastePercent: number;
  finalAmount: number;
}

interface Material {
  id: string;
  name: string;
  sku: string;
  type: 'metal' | 'wood' | 'plastic' | 'glass' | 'fabric' | 'other';
  unit: string;
  pricePerUnit: number;
}

const materials: Material[] = [
  { id: '1', name: 'Сталь листова 2мм', sku: 'STL-002', type: 'metal', unit: 'кг', pricePerUnit: 45 },
  { id: '2', name: 'Сталь листова 3мм', sku: 'STL-003', type: 'metal', unit: 'кг', pricePerUnit: 48 },
  { id: '3', name: 'Алюміній листовий', sku: 'ALU-001', type: 'metal', unit: 'кг', pricePerUnit: 120 },
  { id: '4', name: 'Труба квадратна 40×40', sku: 'TUBE-4040', type: 'metal', unit: 'м', pricePerUnit: 85 },
  { id: '5', name: 'Дошка дубова', sku: 'WOOD-OAK', type: 'wood', unit: 'м³', pricePerUnit: 25000 },
  { id: '6', name: 'ДСП 18мм', sku: 'DSP-018', type: 'wood', unit: 'м²', pricePerUnit: 180 },
  { id: '7', name: 'МДФ 16мм', sku: 'MDF-016', type: 'wood', unit: 'м²', pricePerUnit: 220 },
  { id: '8', name: 'Пластик ABS', sku: 'PLS-ABS', type: 'plastic', unit: 'кг', pricePerUnit: 65 },
  { id: '9', name: 'Скло загартоване 4мм', sku: 'GLS-004', type: 'glass', unit: 'м²', pricePerUnit: 450 },
  { id: '10', name: 'Тканина оббивна', sku: 'FAB-001', type: 'fabric', unit: 'м²', pricePerUnit: 350 },
];

export function SmartBOMCalculator({ onBack, onSave }: { onBack: () => void; onSave: () => void }) {
  const [items, setItems] = useState<BOMItem[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [selectedCalculator, setSelectedCalculator] = useState<CalculatorType | null>(null);
  const [parameters, setParameters] = useState<Record<string, number>>({});
  const [isCalculatorOpen, setIsCalculatorOpen] = useState(false);

  // Розрахунок кількості матеріалу
  const calculateAmount = () => {
    if (!selectedCalculator) return 0;

    const calc = selectedCalculator;
    let result = 0;

    switch (calc.id) {
      case 'metal_sheet':
        result = (parameters.length * parameters.width) / 1000000 * parameters.thickness * parameters.density / 1000;
        break;
      case 'metal_tube':
        result = (parameters.length / 1000) * parameters.weight_per_meter;
        break;
      case 'metal_rod':
        result = (3.14159 * parameters.diameter * parameters.diameter / 4) * parameters.length * parameters.density / 1000000 / 1000;
        break;
      case 'wood_board':
        result = (parameters.length * parameters.width * parameters.thickness) / 1000000000;
        break;
      case 'wood_panel':
      case 'glass_sheet':
        result = (parameters.length * parameters.width) / 1000000;
        break;
      case 'plastic_sheet':
        result = (parameters.length * parameters.width * parameters.thickness) / 1000000000 * parameters.density;
        break;
      case 'fabric':
        result = (parameters.length * parameters.width) / 1000000;
        break;
      default:
        result = 0;
    }

    return result;
  };

  // Додавання елемента до BOM
  const handleAddItem = () => {
    if (!selectedMaterial || !selectedCalculator) {
      toast.error('Оберіть матеріал та тип калькулятора');
      return;
    }

    const calculatedAmount = calculateAmount();
    const wasteAmount = calculatedAmount * (selectedCalculator.wastePercent / 100);
    const finalAmount = calculatedAmount + wasteAmount;
    const totalPrice = finalAmount * selectedMaterial.pricePerUnit;

    const newItem: BOMItem = {
      id: Date.now().toString(),
      materialId: selectedMaterial.id,
      materialName: selectedMaterial.name,
      calculatorType: selectedCalculator.id,
      parameters: { ...parameters },
      calculatedAmount,
      unit: selectedMaterial.unit,
      pricePerUnit: selectedMaterial.pricePerUnit,
      totalPrice,
      wastePercent: selectedCalculator.wastePercent,
      finalAmount,
    };

    setItems(prev => [...prev, newItem]);
    setIsCalculatorOpen(false);
    toast.success('Компонент додано до специфікації');
  };

  // Видалення елемента
  const handleRemoveItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  // Копіювання елемента
  const handleDuplicateItem = (item: BOMItem) => {
    const newItem = {
      ...item,
      id: Date.now().toString(),
    };
    setItems(prev => [...prev, newItem]);
  };

  // Застосування пресету розмірів
  const applySizePreset = (preset: SizePreset) => {
    setParameters(preset.dimensions);
  };

  // Вибір матеріалу та калькулятора
  const handleMaterialSelect = (materialId: string) => {
    const material = materials.find(m => m.id === materialId);
    if (material) {
      setSelectedMaterial(material);
      // Автоматично вибираємо перший відповідний калькулятор
      const suitableCalculator = calculatorTemplates.find(c => c.materialType === material.type);
      if (suitableCalculator) {
        setSelectedCalculator(suitableCalculator);
        // Ініціалізуємо параметри значеннями за замовчуванням
        const defaultParams: Record<string, number> = {};
        suitableCalculator.parameters.forEach(p => {
          defaultParams[p.key] = p.defaultValue || 0;
        });
        setParameters(defaultParams);
      }
    }
  };

  const totalCost = items.reduce((sum, item) => sum + item.totalPrice, 0);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onBack} className="h-8 w-8">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Розумна специфікація (BOM)</h2>
            <p className="text-xs text-slate-500">Автоматичний розрахунок матеріалів за розмірами</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onBack}>
            Скасувати
          </Button>
          <Button size="sm" onClick={onSave} className="bg-indigo-600 hover:bg-indigo-700">
            <Save className="w-3.5 h-3.5 mr-1.5" />
            Зберегти
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Panel - BOM List */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold">Компоненти специфікації</h3>
                <p className="text-xs text-slate-500">{items.length} компонентів</p>
              </div>
              <Dialog open={isCalculatorOpen} onOpenChange={setIsCalculatorOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">
                    <Plus className="w-3.5 h-3.5 mr-1" />
                    Додати компонент
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-auto">
                  <DialogHeader>
                    <DialogTitle className="text-base flex items-center gap-2">
                      <Calculator className="w-5 h-5" />
                      Розумний калькулятор матеріалів
                    </DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    {/* Material Selection */}
                    <div className="space-y-2">
                      <Label className="text-xs">Матеріал</Label>
                      <Select onValueChange={handleMaterialSelect}>
                        <SelectTrigger className="h-9 text-sm">
                          <SelectValue placeholder="Оберіть матеріал" />
                        </SelectTrigger>
                        <SelectContent>
                          {materials.map(m => (
                            <SelectItem key={m.id} value={m.id}>
                              <div className="flex items-center justify-between w-full">
                                <span>{m.name}</span>
                                <span className="text-xs text-slate-400 ml-4">{m.sku}</span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Calculator Type */}
                    {selectedMaterial && (
                      <div className="space-y-2">
                        <Label className="text-xs">Тип калькулятора</Label>
                        <Select 
                          value={selectedCalculator?.id} 
                          onValueChange={(id) => {
                            const calc = calculatorTemplates.find(c => c.id === id);
                            setSelectedCalculator(calc || null);
                            if (calc) {
                              const defaultParams: Record<string, number> = {};
                              calc.parameters.forEach(p => {
                                defaultParams[p.key] = p.defaultValue || 0;
                              });
                              setParameters(defaultParams);
                            }
                          }}
                        >
                          <SelectTrigger className="h-9 text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {calculatorTemplates
                              .filter(c => c.materialType === selectedMaterial.type)
                              .map(c => (
                                <SelectItem key={c.id} value={c.id}>
                                  {c.name}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {/* Size Presets */}
                    {selectedCalculator && sizePresets[selectedCalculator.id] && (
                      <div className="space-y-2">
                        <Label className="text-xs">Швидкий вибір розміру</Label>
                        <div className="flex flex-wrap gap-2">
                          {sizePresets[selectedCalculator.id].map((preset, i) => (
                            <Button
                              key={i}
                              variant="outline"
                              size="sm"
                              className="text-xs h-7"
                              onClick={() => applySizePreset(preset)}
                            >
                              {preset.name}
                            </Button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Parameters */}
                    {selectedCalculator && (
                      <div className="space-y-3 p-3 bg-slate-50 rounded-lg">
                        <Label className="text-xs font-medium">Параметри виробу</Label>
                        <div className="grid grid-cols-2 gap-3">
                          {selectedCalculator.parameters.map(param => (
                            <div key={param.key} className="space-y-1">
                              <Label className="text-[10px] text-slate-500">
                                {param.name} ({param.unit})
                              </Label>
                              <Input
                                type="number"
                                value={parameters[param.key] || ''}
                                onChange={(e) => setParameters(prev => ({
                                  ...prev,
                                  [param.key]: parseFloat(e.target.value) || 0
                                }))}
                                className="h-8 text-sm"
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Calculation Preview */}
                    {selectedCalculator && (
                      <div className="space-y-2 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-600">Розрахована кількість:</span>
                          <span className="text-lg font-bold text-indigo-700">
                            {calculateAmount().toFixed(3)} {selectedMaterial?.unit}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-600">Відходи ({selectedCalculator.wastePercent}%):</span>
                          <span className="text-sm text-amber-600">
                            +{(calculateAmount() * selectedCalculator.wastePercent / 100).toFixed(3)} {selectedMaterial?.unit}
                          </span>
                        </div>
                        <div className="flex items-center justify-between pt-2 border-t border-indigo-100">
                          <span className="text-xs font-medium text-slate-700">Разом з відходами:</span>
                          <span className="text-lg font-bold text-emerald-600">
                            {(calculateAmount() * (1 + selectedCalculator.wastePercent / 100)).toFixed(3)} {selectedMaterial?.unit}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-600">Вартість:</span>
                          <span className="text-lg font-bold text-slate-900">
                            {((calculateAmount() * (1 + selectedCalculator.wastePercent / 100)) * (selectedMaterial?.pricePerUnit || 0)).toFixed(2)} ₴
                          </span>
                        </div>
                      </div>
                    )}

                    <Button 
                      onClick={handleAddItem} 
                      className="w-full bg-indigo-600 hover:bg-indigo-700"
                      disabled={!selectedMaterial || !selectedCalculator}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Додати до специфікації
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* BOM Items Table */}
            {items.length > 0 ? (
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr className="h-9">
                      <th className="px-3 text-left text-xs font-medium text-slate-600">№</th>
                      <th className="px-3 text-left text-xs font-medium text-slate-600">Матеріал</th>
                      <th className="px-3 text-left text-xs font-medium text-slate-600">Розміри</th>
                      <th className="px-3 text-right text-xs font-medium text-slate-600">Кількість</th>
                      <th className="px-3 text-right text-xs font-medium text-slate-600">Відходи</th>
                      <th className="px-3 text-right text-xs font-medium text-slate-600">Разом</th>
                      <th className="px-3 text-right text-xs font-medium text-slate-600">Ціна</th>
                      <th className="px-3 text-center text-xs font-medium text-slate-600 w-20">Дії</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item, index) => (
                      <tr key={item.id} className="border-t hover:bg-slate-50 h-12">
                        <td className="px-3 text-sm">{index + 1}</td>
                        <td className="px-3">
                          <div>
                            <p className="text-sm font-medium">{item.materialName}</p>
                            <p className="text-[10px] text-slate-400">{item.calculatorType}</p>
                          </div>
                        </td>
                        <td className="px-3">
                          <span className="text-xs text-slate-600">
                            {Object.entries(item.parameters)
                              .slice(0, 3)
                              .map(([, v]) => `${v}`)
                              .join('×')} мм
                          </span>
                        </td>
                        <td className="px-3 text-right">
                          <span className="text-sm">{item.calculatedAmount.toFixed(3)}</span>
                          <span className="text-xs text-slate-400 ml-1">{item.unit}</span>
                        </td>
                        <td className="px-3 text-right">
                          <Badge variant="secondary" className="text-[10px]">
                            +{item.wastePercent}%
                          </Badge>
                        </td>
                        <td className="px-3 text-right">
                          <span className="text-sm font-medium">{item.finalAmount.toFixed(3)}</span>
                          <span className="text-xs text-slate-400 ml-1">{item.unit}</span>
                        </td>
                        <td className="px-3 text-right">
                          <span className="text-sm font-medium">{item.totalPrice.toFixed(2)}</span>
                          <span className="text-xs text-slate-400 ml-1">₴</span>
                        </td>
                        <td className="px-3 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-7 w-7"
                              onClick={() => handleDuplicateItem(item)}
                            >
                              <Copy className="w-3.5 h-3.5 text-slate-400" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-7 w-7"
                              onClick={() => handleRemoveItem(item.id)}
                            >
                              <Trash2 className="w-3.5 h-3.5 text-rose-400" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-lg">
                <Layers className="w-12 h-12 text-slate-200 mx-auto mb-3" />
                <p className="text-sm text-slate-500">Специфікація порожня</p>
                <p className="text-xs text-slate-400 mb-4">Додайте компоненти за допомогою розумного калькулятора</p>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => setIsCalculatorOpen(true)}
                >
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати перший компонент
                </Button>
              </div>
            )}
          </Card>
        </div>

        {/* Right Panel - Summary */}
        <div className="space-y-4">
          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Підсумок вартості
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Матеріали:</span>
                <span>{items.length} позицій</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Загальна вага:</span>
                <span>
                  {items.filter(i => i.unit === 'кг').reduce((s, i) => s + i.finalAmount, 0).toFixed(2)} кг
                </span>
              </div>
              <div className="border-t pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Всього по специфікації:</span>
                  <span className="text-xl font-bold text-indigo-600">{totalCost.toFixed(2)} ₴</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Info className="w-4 h-4" />
              Довідка
            </h3>
            <div className="space-y-2 text-xs text-slate-600">
              <p>• Виберіть матеріал та тип калькулятора</p>
              <p>• Введіть розміри виробу в мм</p>
              <p>• Система автоматично розрахує кількість</p>
              <p>• Враховуються відходи на різку/обробку</p>
              <p>• Використовуйте пресети для швидкого вводу</p>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="text-sm font-semibold mb-3">Доступні калькулятори</h3>
            <div className="space-y-2">
              {calculatorTemplates.map(calc => (
                <div key={calc.id} className="flex items-center gap-2 text-xs">
                  <Badge variant="secondary" className="text-[10px]">
                    {calc.materialType}
                  </Badge>
                  <span className="text-slate-600">{calc.name}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
