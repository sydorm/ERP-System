import { useState } from 'react';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Edit2, 
  GripVertical,
  Tag,
  Layers,
  Search,
  Save,
  CheckCircle2,
  Hash,
  Type,
  List,
  ToggleLeft,
  Calendar,
  Ruler
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
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface Characteristic {
  id: string;
  name: string;
  type: 'text' | 'number' | 'select' | 'multiselect' | 'boolean' | 'date' | 'dimension';
  unit?: string;
  options?: string[];
  required: boolean;
  showInFilter: boolean;
  showInTable: boolean;
  order: number;
}

interface Category {
  id: string;
  name: string;
  characteristics: Characteristic[];
}

const characteristicTypes = [
  { value: 'text', label: 'Текст', icon: Type },
  { value: 'number', label: 'Число', icon: Hash },
  { value: 'select', label: 'Випадаючий список', icon: List },
  { value: 'multiselect', label: 'Мультивибір', icon: Layers },
  { value: 'boolean', label: 'Так/Ні', icon: ToggleLeft },
  { value: 'date', label: 'Дата', icon: Calendar },
  { value: 'dimension', label: 'Розміри (Д×Ш×В)', icon: Ruler },
];

const initialCategories: Category[] = [
  {
    id: '1',
    name: 'Меблі',
    characteristics: [
      { id: '1', name: 'Матеріал', type: 'select', options: ['Дуб', 'Бук', 'Сосна', 'МДФ', 'ДСП'], required: true, showInFilter: true, showInTable: true, order: 1 },
      { id: '2', name: 'Колір', type: 'select', options: ['Білий', 'Чорний', 'Горіх', 'Дуб'], required: true, showInFilter: true, showInTable: true, order: 2 },
      { id: '3', name: 'Висота', type: 'number', unit: 'мм', required: false, showInFilter: true, showInTable: false, order: 3 },
      { id: '4', name: 'Ширина', type: 'number', unit: 'мм', required: false, showInFilter: true, showInTable: false, order: 4 },
      { id: '5', name: 'Глибина', type: 'number', unit: 'мм', required: false, showInFilter: false, showInTable: false, order: 5 },
      { id: '6', name: 'Вага', type: 'number', unit: 'кг', required: false, showInFilter: false, showInTable: true, order: 6 },
    ],
  },
  {
    id: '2',
    name: 'Металоконструкції',
    characteristics: [
      { id: '7', name: 'Тип металу', type: 'select', options: ['Сталь', 'Алюміній', 'Нержавійка'], required: true, showInFilter: true, showInTable: true, order: 1 },
      { id: '8', name: 'Товщина', type: 'number', unit: 'мм', required: true, showInFilter: true, showInTable: true, order: 2 },
      { id: '9', name: 'Покриття', type: 'select', options: ['Фарба', 'Порошок', 'Цинк', 'Без покриття'], required: false, showInFilter: true, showInTable: false, order: 3 },
      { id: '10', name: 'Габарити', type: 'dimension', required: true, showInFilter: false, showInTable: true, order: 4 },
    ],
  },
  {
    id: '3',
    name: 'Фурнітура',
    characteristics: [
      { id: '11', name: 'Тип', type: 'select', options: ['Петля', 'Ручка', 'Напрямна', 'Замок'], required: true, showInFilter: true, showInTable: true, order: 1 },
      { id: '12', name: 'Матеріал', type: 'select', options: ['Метал', 'Пластик', 'Дерево'], required: true, showInFilter: true, showInTable: false, order: 2 },
      { id: '13', name: 'Виробник', type: 'select', options: ['Hettich', 'Blum', 'GTV', 'Інше'], required: false, showInFilter: true, showInTable: true, order: 3 },
    ],
  },
];

export function CharacteristicsSettings({ onBack }: { onBack: () => void }) {
  const [categories, setCategories] = useState<Category[]>(initialCategories);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('1');
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [editingCharacteristic, setEditingCharacteristic] = useState<Characteristic | null>(null);

  const selectedCategory = categories.find(c => c.id === selectedCategoryId);

  const [newCharacteristic, setNewCharacteristic] = useState<Partial<Characteristic>>({
    type: 'text',
    required: false,
    showInFilter: true,
    showInTable: false,
  });

  const handleSaveCharacteristic = () => {
    if (!newCharacteristic.name) {
      toast.error('Введіть назву характеристики');
      return;
    }

    const characteristic: Characteristic = {
      id: editingCharacteristic?.id || Date.now().toString(),
      name: newCharacteristic.name || '',
      type: (newCharacteristic.type as any) || 'text',
      unit: newCharacteristic.unit,
      options: newCharacteristic.options,
      required: newCharacteristic.required || false,
      showInFilter: newCharacteristic.showInFilter || false,
      showInTable: newCharacteristic.showInTable || false,
      order: editingCharacteristic?.order || (selectedCategory?.characteristics.length || 0) + 1,
    };

    setCategories(prev => prev.map(cat => {
      if (cat.id === selectedCategoryId) {
        if (editingCharacteristic) {
          return {
            ...cat,
            characteristics: cat.characteristics.map(ch => 
              ch.id === editingCharacteristic.id ? characteristic : ch
            ),
          };
        } else {
          return {
            ...cat,
            characteristics: [...cat.characteristics, characteristic],
          };
        }
      }
      return cat;
    }));

    toast.success(editingCharacteristic ? 'Характеристику оновлено' : 'Характеристику додано');
    setIsAddDialogOpen(false);
    setEditingCharacteristic(null);
    setNewCharacteristic({ type: 'text', required: false, showInFilter: true, showInTable: false });
  };

  const handleDeleteCharacteristic = (id: string) => {
    setCategories(prev => prev.map(cat => {
      if (cat.id === selectedCategoryId) {
        return {
          ...cat,
          characteristics: cat.characteristics.filter(ch => ch.id !== id),
        };
      }
      return cat;
    }));
    toast.success('Характеристику видалено');
  };

  const handleEditCharacteristic = (ch: Characteristic) => {
    setEditingCharacteristic(ch);
    setNewCharacteristic(ch);
    setIsAddDialogOpen(true);
  };

  const handleAddOption = (option: string) => {
    if (!option.trim()) return;
    setNewCharacteristic(prev => ({
      ...prev,
      options: [...(prev.options || []), option.trim()],
    }));
  };

  const handleRemoveOption = (index: number) => {
    setNewCharacteristic(prev => ({
      ...prev,
      options: prev.options?.filter((_, i) => i !== index) || [],
    }));
  };

  const filteredCharacteristics = selectedCategory?.characteristics.filter(ch =>
    ch.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow-sm">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={onBack} className="h-8 w-8">
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Налаштування характеристик</h2>
            <p className="text-xs text-slate-500">Довідник характеристик за категоріями</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onBack}>
            Скасувати
          </Button>
          <Button size="sm" onClick={() => toast.success('Зміни збережено')} className="bg-indigo-600 hover:bg-indigo-700">
            <Save className="w-3.5 h-3.5 mr-1.5" />
            Зберегти
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Categories Sidebar */}
        <Card className="lg:col-span-1 p-3">
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-slate-500" />
            <h3 className="text-sm font-semibold">Категорії</h3>
          </div>
          <div className="space-y-1">
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategoryId(cat.id)}
                className={cn(
                  'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all',
                  selectedCategoryId === cat.id
                    ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                    : 'hover:bg-slate-50 text-slate-700'
                )}
              >
                <span>{cat.name}</span>
                <Badge variant="secondary" className="text-[10px]">
                  {cat.characteristics.length}
                </Badge>
              </button>
            ))}
          </div>
          <Button variant="outline" size="sm" className="w-full mt-3 text-xs">
            <Plus className="w-3.5 h-3.5 mr-1" />
            Нова категорія
          </Button>
        </Card>

        {/* Characteristics List */}
        <Card className="lg:col-span-3 p-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold">{selectedCategory?.name}</h3>
              <p className="text-xs text-slate-500">Налаштуйте характеристики для цієї категорії</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input 
                  placeholder="Пошук..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 h-8 text-sm w-48"
                />
              </div>
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">
                    <Plus className="w-3.5 h-3.5 mr-1" />
                    Додати
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-lg">
                  <DialogHeader>
                    <DialogTitle className="text-base">
                      {editingCharacteristic ? 'Редагувати характеристику' : 'Нова характеристика'}
                    </DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label className="text-xs">Назва характеристики</Label>
                      <Input 
                        placeholder="Наприклад: Матеріал, Колір, Висота..."
                        value={newCharacteristic.name || ''}
                        onChange={(e) => setNewCharacteristic(prev => ({ ...prev, name: e.target.value }))}
                        className="h-9 text-sm"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs">Тип даних</Label>
                      <Select 
                        value={newCharacteristic.type} 
                        onValueChange={(v) => setNewCharacteristic(prev => ({ ...prev, type: v as any }))}
                      >
                        <SelectTrigger className="h-9 text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {characteristicTypes.map(type => (
                            <SelectItem key={type.value} value={type.value}>
                              <div className="flex items-center gap-2">
                                <type.icon className="w-4 h-4" />
                                {type.label}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {(newCharacteristic.type === 'number' || newCharacteristic.type === 'dimension') && (
                      <div className="space-y-2">
                        <Label className="text-xs">Одиниця виміру</Label>
                        <Input 
                          placeholder="мм, кг, см..."
                          value={newCharacteristic.unit || ''}
                          onChange={(e) => setNewCharacteristic(prev => ({ ...prev, unit: e.target.value }))}
                          className="h-9 text-sm"
                        />
                      </div>
                    )}

                    {(newCharacteristic.type === 'select' || newCharacteristic.type === 'multiselect') && (
                      <div className="space-y-2">
                        <Label className="text-xs">Варіанти значень</Label>
                        <div className="flex gap-2">
                          <Input 
                            placeholder="Додати варіант..."
                            className="h-9 text-sm flex-1"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                handleAddOption((e.target as HTMLInputElement).value);
                                (e.target as HTMLInputElement).value = '';
                              }
                            }}
                          />
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={(e) => {
                              const input = (e.target as HTMLElement).previousElementSibling as HTMLInputElement;
                              handleAddOption(input.value);
                              input.value = '';
                            }}
                          >
                            Додати
                          </Button>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {newCharacteristic.options?.map((opt, i) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {opt}
                              <button 
                                onClick={() => handleRemoveOption(i)}
                                className="ml-1 text-slate-400 hover:text-rose-500"
                              >
                                ×
                              </button>
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="space-y-3 pt-2 border-t">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">Обов'язкове поле</p>
                          <p className="text-xs text-slate-500">Характеристика має бути заповнена</p>
                        </div>
                        <Switch 
                          checked={newCharacteristic.required}
                          onCheckedChange={(v) => setNewCharacteristic(prev => ({ ...prev, required: v }))}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">Показувати у фільтрі</p>
                          <p className="text-xs text-slate-500">Доступно для фільтрації товарів</p>
                        </div>
                        <Switch 
                          checked={newCharacteristic.showInFilter}
                          onCheckedChange={(v) => setNewCharacteristic(prev => ({ ...prev, showInFilter: v }))}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">Показувати в таблиці</p>
                          <p className="text-xs text-slate-500">Відображати у списку товарів</p>
                        </div>
                        <Switch 
                          checked={newCharacteristic.showInTable}
                          onCheckedChange={(v) => setNewCharacteristic(prev => ({ ...prev, showInTable: v }))}
                        />
                      </div>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => {
                      setIsAddDialogOpen(false);
                      setEditingCharacteristic(null);
                      setNewCharacteristic({ type: 'text', required: false, showInFilter: true, showInTable: false });
                    }}>
                      Скасувати
                    </Button>
                    <Button onClick={handleSaveCharacteristic} className="bg-indigo-600 hover:bg-indigo-700">
                      {editingCharacteristic ? 'Зберегти' : 'Додати'}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Characteristics Table */}
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr className="h-9">
                  <th className="px-3 text-left text-xs font-medium text-slate-600 w-8">#</th>
                  <th className="px-3 text-left text-xs font-medium text-slate-600">Назва</th>
                  <th className="px-3 text-left text-xs font-medium text-slate-600">Тип</th>
                  <th className="px-3 text-left text-xs font-medium text-slate-600">Од.</th>
                  <th className="px-3 text-center text-xs font-medium text-slate-600">Обов'яз.</th>
                  <th className="px-3 text-center text-xs font-medium text-slate-600">Фільтр</th>
                  <th className="px-3 text-center text-xs font-medium text-slate-600">Таблиця</th>
                  <th className="px-3 text-right text-xs font-medium text-slate-600 w-20">Дії</th>
                </tr>
              </thead>
              <tbody>
                {filteredCharacteristics.map((ch) => (
                  <tr key={ch.id} className="border-t hover:bg-slate-50 h-11">
                    <td className="px-3">
                      <GripVertical className="w-4 h-4 text-slate-300 cursor-move" />
                    </td>
                    <td className="px-3">
                      <span className="text-sm font-medium">{ch.name}</span>
                    </td>
                    <td className="px-3">
                      <Badge variant="secondary" className="text-[10px]">
                        {characteristicTypes.find(t => t.value === ch.type)?.label}
                      </Badge>
                    </td>
                    <td className="px-3">
                      <span className="text-xs text-slate-500">{ch.unit || '-'}</span>
                    </td>
                    <td className="px-3 text-center">
                      {ch.required ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mx-auto" />
                      ) : (
                        <span className="text-slate-300">-</span>
                      )}
                    </td>
                    <td className="px-3 text-center">
                      {ch.showInFilter ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mx-auto" />
                      ) : (
                        <span className="text-slate-300">-</span>
                      )}
                    </td>
                    <td className="px-3 text-center">
                      {ch.showInTable ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 mx-auto" />
                      ) : (
                        <span className="text-slate-300">-</span>
                      )}
                    </td>
                    <td className="px-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-7 w-7"
                          onClick={() => handleEditCharacteristic(ch)}
                        >
                          <Edit2 className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          className="h-7 w-7"
                          onClick={() => handleDeleteCharacteristic(ch.id)}
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

          {filteredCharacteristics.length === 0 && (
            <div className="text-center py-8">
              <Tag className="w-12 h-12 text-slate-200 mx-auto mb-3" />
              <p className="text-sm text-slate-500">Немає характеристик</p>
              <p className="text-xs text-slate-400">Додайте першу характеристику для цієї категорії</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
