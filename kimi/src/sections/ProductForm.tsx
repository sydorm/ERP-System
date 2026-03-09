import { useState } from 'react';
import { 
  ArrowLeft, 
  Save, 
  X, 
  Upload, 
  Image as ImageIcon, 
  Plus,
  Trash2,
  FileText,
  Package,
  DollarSign,
  Layers,
  Warehouse,
  FolderOpen,
  Grid3X3,
  Users,
  RefreshCw,
  ClipboardList,
  MessageSquare,
  Link2,
  Box,
  Settings,
  MoreHorizontal,
  Download,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface ProductFormProps {
  onCancel: () => void;
  onSave: () => void;
}

const tabs = [
  { id: 'general', label: 'Загальна інформація', icon: FileText },
  { id: 'characteristics', label: 'Характеристики', icon: Package },
  { id: 'pricing', label: 'Ціни та Комерція', icon: DollarSign },
  { id: 'bom', label: 'Специфікації (BOM)', icon: Layers },
  { id: 'inventory', label: 'Складські запаси', icon: Warehouse },
  { id: 'files', label: 'Файли', icon: FolderOpen },
  { id: 'variants', label: 'Варіанти', icon: Grid3X3 },
  { id: 'suppliers', label: 'Постачальники', icon: Users },
  { id: 'alternatives', label: 'Альтернативи', icon: RefreshCw },
  { id: 'production', label: 'Виробництво', icon: Settings },
  { id: 'packaging', label: 'Упаковка', icon: Box },
  { id: 'history', label: 'Історія', icon: ClipboardList },
  { id: 'notes', label: 'Нотатки', icon: MessageSquare },
  { id: 'related', label: 'Пов\'язані товари', icon: Link2 },
];

export function ProductForm({ onCancel, onSave }: ProductFormProps) {
  const [activeTab, setActiveTab] = useState('general');
  const [isActive, setIsActive] = useState(true);
  const [isTrackInventory, setIsTrackInventory] = useState(true);

  const handleSave = () => {
    toast.success('Товар успішно збережено');
    onSave();
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onCancel} className="h-8 w-8">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Новий товар</h2>
            <p className="text-xs text-slate-500">Створення нової номенклатури</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onCancel}>
            <X className="w-3.5 h-3.5 mr-1.5" />
            Скасувати
          </Button>
          <Button size="sm" onClick={handleSave} className="bg-indigo-600 hover:bg-indigo-700">
            <Save className="w-3.5 h-3.5 mr-1.5" />
            Зберегти
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 overflow-x-auto">
          <div className="flex min-w-max">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-3 text-xs font-medium border-b-2 transition-all duration-200 whitespace-nowrap',
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                )}
              >
                <tab.icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-4">
          {/* General Info Tab */}
          {activeTab === 'general' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Main Form */}
              <div className="lg:col-span-2 space-y-4">
                <div className="space-y-2">
                  <Label className="text-xs font-medium">Назва товару <span className="text-rose-500">*</span></Label>
                  <Input 
                    placeholder="Введіть назву (напр., Нога стола чорна 710мм)" 
                    className="h-9 text-sm"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Артикул (SKU) <span className="text-rose-500">*</span></Label>
                    <Input 
                      placeholder="WOOD-001" 
                      className="h-9 text-sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Категорія <span className="text-rose-500">*</span></Label>
                    <Select>
                      <SelectTrigger className="h-9 text-sm">
                        <SelectValue placeholder="Оберіть категорію" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="furniture">Меблі</SelectItem>
                        <SelectItem value="accessories">Аксесуари</SelectItem>
                        <SelectItem value="hardware">Фурнітура</SelectItem>
                        <SelectItem value="materials">Матеріали</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-xs font-medium">Опис товару</Label>
                  <Textarea 
                    placeholder="Докладний опис товару, технічні характеристики..." 
                    className="min-h-[100px] text-sm resize-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Штрихкод (EAN)</Label>
                    <Input 
                      placeholder="1234567890123" 
                      className="h-9 text-sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Внутрішній код</Label>
                    <Input 
                      placeholder="Внутрішній артикул" 
                      className="h-9 text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Вага (кг)</Label>
                    <Input 
                      type="number" 
                      placeholder="0.00" 
                      className="h-9 text-sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Довжина (см)</Label>
                    <Input 
                      type="number" 
                      placeholder="0.00" 
                      className="h-9 text-sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Ширина (см)</Label>
                    <Input 
                      type="number" 
                      placeholder="0.00" 
                      className="h-9 text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Sidebar */}
              <div className="space-y-4">
                {/* Image Upload */}
                <Card className="p-3 border-dashed border-2 border-slate-300">
                  <div className="text-center">
                    <div className="w-12 h-12 mx-auto rounded-lg bg-slate-100 flex items-center justify-center mb-2">
                      <ImageIcon className="w-6 h-6 text-slate-400" />
                    </div>
                    <p className="text-xs text-slate-600 mb-1">Натисніть для завантаження</p>
                    <p className="text-[10px] text-slate-400">PNG, JPG до 5MB</p>
                    <Button variant="outline" size="sm" className="mt-2 text-xs h-7">
                      <Upload className="w-3 h-3 mr-1" />
                      Завантажити
                    </Button>
                  </div>
                </Card>

                {/* Unit */}
                <div className="space-y-2">
                  <Label className="text-xs font-medium">Одиниця виміру</Label>
                  <Select defaultValue="pcs">
                    <SelectTrigger className="h-9 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pcs">Штуки</SelectItem>
                      <SelectItem value="kg">Кілограми</SelectItem>
                      <SelectItem value="m">Метри</SelectItem>
                      <SelectItem value="m2">Кв. метри</SelectItem>
                      <SelectItem value="l">Літри</SelectItem>
                      <SelectItem value="pack">Упаковки</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Status */}
                <div className="space-y-2">
                  <Label className="text-xs font-medium">Статус товару</Label>
                  <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-50">
                    <Switch 
                      checked={isActive} 
                      onCheckedChange={setIsActive}
                    />
                    <span className={cn(
                      'text-xs font-medium',
                      isActive ? 'text-emerald-600' : 'text-slate-500'
                    )}>
                      {isActive ? 'Активний' : 'Неактивний'}
                    </span>
                  </div>
                </div>

                {/* Track Inventory */}
                <div className="space-y-2">
                  <Label className="text-xs font-medium">Облік запасів</Label>
                  <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-50">
                    <Switch 
                      checked={isTrackInventory} 
                      onCheckedChange={setIsTrackInventory}
                    />
                    <span className={cn(
                      'text-xs font-medium',
                      isTrackInventory ? 'text-emerald-600' : 'text-slate-500'
                    )}>
                      {isTrackInventory ? 'Вести облік' : 'Не вести облік'}
                    </span>
                  </div>
                </div>

                {/* Tags */}
                <div className="space-y-2">
                  <Label className="text-xs font-medium">Теги</Label>
                  <div className="flex flex-wrap gap-1">
                    <Badge variant="secondary" className="text-[10px]">Меблі</Badge>
                    <Badge variant="secondary" className="text-[10px]">Дерево</Badge>
                    <Button variant="ghost" size="sm" className="h-5 px-1 text-[10px]">
                      <Plus className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Characteristics Tab */}
          {activeTab === 'characteristics' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">Характеристики товару</h3>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати характеристику
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Назва</TableHead>
                      <TableHead className="text-xs py-2">Значення</TableHead>
                      <TableHead className="text-xs py-2">Одиниця</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Матеріал</TableCell>
                      <TableCell className="text-sm py-2">Дуб масив</TableCell>
                      <TableCell className="text-sm py-2">-</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Колір</TableCell>
                      <TableCell className="text-sm py-2">Горіх</TableCell>
                      <TableCell className="text-sm py-2">-</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Pricing Tab */}
          {activeTab === 'pricing' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card className="p-4">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Ціни закупівлі</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Основна ціна</Label>
                      <Input type="number" placeholder="0.00" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Валюта</Label>
                      <Select defaultValue="uah">
                        <SelectTrigger className="h-8 text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="uah">UAH (₴)</SelectItem>
                          <SelectItem value="usd">USD ($)</SelectItem>
                          <SelectItem value="eur">EUR (€)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Мін. партія для закупівлі</Label>
                    <Input type="number" placeholder="1" className="h-8 text-sm" />
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Ціни продажу</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Роздрібна ціна</Label>
                      <Input type="number" placeholder="0.00" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Оптова ціна</Label>
                      <Input type="number" placeholder="0.00" className="h-8 text-sm" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Спеціальна ціна</Label>
                      <Input type="number" placeholder="0.00" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Надбавка (%)</Label>
                      <Input type="number" placeholder="30" className="h-8 text-sm" />
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-4 lg:col-span-2">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Податки</h3>
                <div className="grid grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Ставка ПДВ</Label>
                    <Select defaultValue="20">
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0">0%</SelectItem>
                        <SelectItem value="7">7%</SelectItem>
                        <SelectItem value="20">20%</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Код УКТЗЕД</Label>
                    <Input placeholder="0000 00 00 00" className="h-8 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Код ТН ВЕД</Label>
                    <Input placeholder="0000 00 000 0" className="h-8 text-sm" />
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* BOM Tab */}
          {activeTab === 'bom' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Специфікація (BOM)</h3>
                  <p className="text-xs text-slate-500">Складові компоненти для виробництва</p>
                </div>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати компонент
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">№</TableHead>
                      <TableHead className="text-xs py-2">Компонент</TableHead>
                      <TableHead className="text-xs py-2">Артикул</TableHead>
                      <TableHead className="text-xs py-2 text-right">Кількість</TableHead>
                      <TableHead className="text-xs py-2">Од.</TableHead>
                      <TableHead className="text-xs py-2 text-right">Ціна</TableHead>
                      <TableHead className="text-xs py-2 text-right">Сума</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">1</TableCell>
                      <TableCell className="text-sm py-2">Дошка дубова 20мм</TableCell>
                      <TableCell className="text-sm py-2">WOOD-002</TableCell>
                      <TableCell className="text-sm py-2 text-right">2.5</TableCell>
                      <TableCell className="text-sm py-2">м²</TableCell>
                      <TableCell className="text-sm py-2 text-right">450.00</TableCell>
                      <TableCell className="text-sm py-2 text-right font-medium">1 125.00</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">2</TableCell>
                      <TableCell className="text-sm py-2">Клей столярний</TableCell>
                      <TableCell className="text-sm py-2">GLUE-001</TableCell>
                      <TableCell className="text-sm py-2 text-right">0.5</TableCell>
                      <TableCell className="text-sm py-2">кг</TableCell>
                      <TableCell className="text-sm py-2 text-right">120.00</TableCell>
                      <TableCell className="text-sm py-2 text-right font-medium">60.00</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
              <div className="flex justify-end">
                <div className="text-right">
                  <p className="text-xs text-slate-500">Всього по специфікації:</p>
                  <p className="text-lg font-bold text-slate-900">1 185.00 ₴</p>
                </div>
              </div>
            </div>
          )}

          {/* Inventory Tab */}
          {activeTab === 'inventory' && (
            <div className="space-y-4">
              <div className="grid grid-cols-4 gap-3">
                <Card className="p-3 text-center">
                  <p className="text-[10px] text-slate-500 uppercase">Всього на складах</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">0</p>
                </Card>
                <Card className="p-3 text-center">
                  <p className="text-[10px] text-slate-500 uppercase">Зарезервовано</p>
                  <p className="text-xl font-bold text-amber-600 mt-1">0</p>
                </Card>
                <Card className="p-3 text-center">
                  <p className="text-[10px] text-slate-500 uppercase">Доступно</p>
                  <p className="text-xl font-bold text-emerald-600 mt-1">0</p>
                </Card>
                <Card className="p-3 text-center">
                  <p className="text-[10px] text-slate-500 uppercase">Мін. запас</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">10</p>
                </Card>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Склад</TableHead>
                      <TableHead className="text-xs py-2 text-right">Кількість</TableHead>
                      <TableHead className="text-xs py-2 text-right">Зарезервовано</TableHead>
                      <TableHead className="text-xs py-2 text-right">Доступно</TableHead>
                      <TableHead className="text-xs py-2 text-right">Мін. запас</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Головний склад</TableCell>
                      <TableCell className="text-sm py-2 text-right">0</TableCell>
                      <TableCell className="text-sm py-2 text-right">0</TableCell>
                      <TableCell className="text-sm py-2 text-right">0</TableCell>
                      <TableCell className="text-sm py-2 text-right">10</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">Мінімальний запас</Label>
                  <Input type="number" placeholder="10" className="h-8 text-sm" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Максимальний запас</Label>
                  <Input type="number" placeholder="100" className="h-8 text-sm" />
                </div>
              </div>
            </div>
          )}

          {/* Files Tab */}
          {activeTab === 'files' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">Прикріплені файли</h3>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Upload className="w-3.5 h-3.5 mr-1" />
                  Завантажити файл
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Файл</TableHead>
                      <TableHead className="text-xs py-2">Тип</TableHead>
                      <TableHead className="text-xs py-2">Розмір</TableHead>
                      <TableHead className="text-xs py-2">Дата</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-blue-500" />
                        Технічний_паспорт.pdf
                      </TableCell>
                      <TableCell className="text-sm py-2">PDF</TableCell>
                      <TableCell className="text-sm py-2">2.4 MB</TableCell>
                      <TableCell className="text-sm py-2">07.03.2026</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Download className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Variants Tab */}
          {activeTab === 'variants' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Варіанти товару</h3>
                  <p className="text-xs text-slate-500">Різні варіації одного товару (розмір, колір)</p>
                </div>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати варіант
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Варіант</TableHead>
                      <TableHead className="text-xs py-2">Артикул</TableHead>
                      <TableHead className="text-xs py-2 text-right">Ціна</TableHead>
                      <TableHead className="text-xs py-2 text-right">Запас</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Чорний / 710мм</TableCell>
                      <TableCell className="text-sm py-2">WOOD-001-B-710</TableCell>
                      <TableCell className="text-sm py-2 text-right">450.00 ₴</TableCell>
                      <TableCell className="text-sm py-2 text-right">25</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Білий / 710мм</TableCell>
                      <TableCell className="text-sm py-2">WOOD-001-W-710</TableCell>
                      <TableCell className="text-sm py-2 text-right">450.00 ₴</TableCell>
                      <TableCell className="text-sm py-2 text-right">18</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Suppliers Tab */}
          {activeTab === 'suppliers' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">Постачальники</h3>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати постачальника
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Постачальник</TableHead>
                      <TableHead className="text-xs py-2">Артикул у постачальника</TableHead>
                      <TableHead className="text-xs py-2 text-right">Ціна закупівлі</TableHead>
                      <TableHead className="text-xs py-2 text-right">Мін. замовлення</TableHead>
                      <TableHead className="text-xs py-2">Термін поставки</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">ТОВ "Лісові Матеріали"</TableCell>
                      <TableCell className="text-sm py-2">LM-2024-001</TableCell>
                      <TableCell className="text-sm py-2 text-right">380.00 ₴</TableCell>
                      <TableCell className="text-sm py-2 text-right">10</TableCell>
                      <TableCell className="text-sm py-2">3-5 днів</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Alternatives Tab */}
          {activeTab === 'alternatives' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">Альтернативні товари (замінники)</h3>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати альтернативу
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Товар</TableHead>
                      <TableHead className="text-xs py-2">Артикул</TableHead>
                      <TableHead className="text-xs py-2 text-right">Ціна</TableHead>
                      <TableHead className="text-xs py-2 text-right">Пріоритет</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Нога стола металева</TableCell>
                      <TableCell className="text-sm py-2">MET-001</TableCell>
                      <TableCell className="text-sm py-2 text-right">320.00 ₴</TableCell>
                      <TableCell className="text-sm py-2 text-right">2</TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Production Tab */}
          {activeTab === 'production' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card className="p-4">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Налаштування виробництва</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                    <div>
                      <p className="text-xs font-medium">Товар для виробництва</p>
                      <p className="text-[10px] text-slate-500">Виробляється на виробництві</p>
                    </div>
                    <Switch />
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                    <div>
                      <p className="text-xs font-medium">Купується</p>
                      <p className="text-[10px] text-slate-500">Можна закуповувати у постачальників</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Час виробництва (годин)</Label>
                    <Input type="number" placeholder="2.5" className="h-8 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Робочий центр</Label>
                    <Select>
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue placeholder="Оберіть центр" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="carpentry">Столярний цех</SelectItem>
                        <SelectItem value="painting">Фарбувальний цех</SelectItem>
                        <SelectItem value="assembly">Збірний цех</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Норми витрат</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Норма часу (год)</Label>
                      <Input type="number" placeholder="1.5" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Вартість роботи (₴)</Label>
                      <Input type="number" placeholder="150.00" className="h-8 text-sm" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Надбавка на відходи (%)</Label>
                    <Input type="number" placeholder="5" className="h-8 text-sm" />
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Packaging Tab */}
          {activeTab === 'packaging' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card className="p-4">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Параметри упаковки</h3>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Вага з упаковкою (кг)</Label>
                      <Input type="number" placeholder="0.00" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Кількість в упаковці</Label>
                      <Input type="number" placeholder="1" className="h-8 text-sm" />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Довжина (см)</Label>
                      <Input type="number" placeholder="0" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Ширина (см)</Label>
                      <Input type="number" placeholder="0" className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Висота (см)</Label>
                      <Input type="number" placeholder="0" className="h-8 text-sm" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Об'єм (м³)</Label>
                    <Input type="number" placeholder="0.000" className="h-8 text-sm" disabled />
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Тип упаковки</h3>
                <div className="space-y-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Тип упаковки</Label>
                    <Select>
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue placeholder="Оберіть тип" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="box">Картонна коробка</SelectItem>
                        <SelectItem value="film">Стрейч-плівка</SelectItem>
                        <SelectItem value="pallet">Палета</SelectItem>
                        <SelectItem value="none">Без упаковки</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Код упаковки</Label>
                    <Input placeholder="PACK-001" className="h-8 text-sm" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Опис упаковки</Label>
                    <Textarea placeholder="Опис упаковки та маркування..." className="min-h-[60px] text-sm resize-none" />
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900">Історія змін</h3>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Дата</TableHead>
                      <TableHead className="text-xs py-2">Користувач</TableHead>
                      <TableHead className="text-xs py-2">Дія</TableHead>
                      <TableHead className="text-xs py-2">Зміни</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">07.03.2026 14:30</TableCell>
                      <TableCell className="text-sm py-2">Адміністратор</TableCell>
                      <TableCell className="text-sm py-2">
                        <Badge variant="secondary" className="text-[10px]">Створення</Badge>
                      </TableCell>
                      <TableCell className="text-sm py-2">Товар створено</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Notes Tab */}
          {activeTab === 'notes' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-900">Нотатки та коментарі</h3>
              <div className="space-y-3">
                <Textarea 
                  placeholder="Додайте нотатку..." 
                  className="min-h-[80px] text-sm resize-none"
                />
                <div className="flex justify-end">
                  <Button size="sm" className="h-7 text-xs">
                    <Plus className="w-3.5 h-3.5 mr-1" />
                    Додати нотатку
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Card className="p-3">
                  <div className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-bold text-indigo-600">А</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium">Адміністратор</span>
                        <span className="text-[10px] text-slate-400">07.03.2026 14:30</span>
                      </div>
                      <p className="text-xs text-slate-600">Потрібно перевірити якість матеріалу перед запуском в виробництво.</p>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* Related Products Tab */}
          {activeTab === 'related' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">Пов'язані товари</h3>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Додати пов'язаний товар
                </Button>
              </div>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 h-8">
                      <TableHead className="text-xs py-2">Товар</TableHead>
                      <TableHead className="text-xs py-2">Артикул</TableHead>
                      <TableHead className="text-xs py-2">Тип зв'язку</TableHead>
                      <TableHead className="w-10 py-2"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="h-10">
                      <TableCell className="text-sm py-2">Стільниця дубова</TableCell>
                      <TableCell className="text-sm py-2">WOOD-010</TableCell>
                      <TableCell className="text-sm py-2">
                        <Badge variant="secondary" className="text-[10px]">Комплект</Badge>
                      </TableCell>
                      <TableCell className="py-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Trash2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
