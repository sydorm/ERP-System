import { useState } from 'react';
import {
  Search,
  MoreHorizontal,
  Edit2,
  Trash2,
  Eye,
  Grid3X3,
  List,
  ChevronLeft,
  ChevronRight,
  ImageIcon,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';

interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  stock: number;
  price: number;
  image?: string;
}

const products: Product[] = [
  {
    id: '1',
    sku: '123',
    name: 'Консоль',
    category: 'Полички для взуття',
    stock: 0,
    price: 0,
  },
  {
    id: '2',
    sku: '1234',
    name: 'Банкетка Loren',
    category: 'Полички для взуття',
    stock: 0,
    price: 0,
  },
];

const categories = ['Всі', 'Полички для взуття', 'Меблі', 'Аксесуари'];

export function ProductsTable() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Всі');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  const filteredProducts = products.filter((product) => {
    const matchesSearch =
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === 'Всі' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between bg-white p-3 rounded-lg shadow-sm">
        <div className="flex flex-col sm:flex-row gap-2 flex-1 w-full">
          {/* Search */}
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Пошук товарів..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-8 text-sm bg-slate-50 border-slate-200 focus:bg-white transition-colors"
            />
          </div>

          {/* Category Filter */}
          <div className="flex gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={cn(
                  'px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all duration-200',
                  selectedCategory === category
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                )}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode('table')}
            className={cn(
              'p-1.5 rounded-md transition-all duration-200',
              viewMode === 'table'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            )}
          >
            <List className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={cn(
              'p-1.5 rounded-md transition-all duration-200',
              viewMode === 'grid'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            )}
          >
            <Grid3X3 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-slate-200">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/50 hover:bg-slate-50/50 h-9">
                <TableHead className="w-12 text-center py-2 text-xs">Фото</TableHead>
                <TableHead className="font-semibold text-slate-700 py-2 text-xs">Артикул</TableHead>
                <TableHead className="font-semibold text-slate-700 py-2 text-xs">Назва</TableHead>
                <TableHead className="font-semibold text-slate-700 py-2 text-xs">Категорія</TableHead>
                <TableHead className="font-semibold text-slate-700 py-2 text-xs text-right">Запас</TableHead>
                <TableHead className="font-semibold text-slate-700 py-2 text-xs text-right">Ціна</TableHead>
                <TableHead className="w-10 py-2"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredProducts.map((product) => (
                <TableRow
                  key={product.id}
                  className="group hover:bg-slate-50/80 transition-colors h-12"
                >
                  <TableCell className="text-center py-2">
                    <div className="w-8 h-8 mx-auto rounded bg-slate-100 flex items-center justify-center">
                      <ImageIcon className="w-4 h-4 text-slate-400" />
                    </div>
                  </TableCell>
                  <TableCell className="font-medium text-slate-900 py-2 text-sm">
                    {product.sku}
                  </TableCell>
                  <TableCell className="py-2">
                    <span className="font-medium text-slate-900 text-sm">{product.name}</span>
                  </TableCell>
                  <TableCell className="py-2">
                    <Badge
                      variant="secondary"
                      className="bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs py-0.5"
                    >
                      {product.category}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right py-2">
                    <span
                      className={cn(
                        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                        product.stock === 0
                          ? 'bg-rose-100 text-rose-700'
                          : product.stock < 10
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-emerald-100 text-emerald-700'
                      )}
                    >
                      {product.stock} шт
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-medium text-slate-900 py-2 text-sm">
                    {product.price} грн
                  </TableCell>
                  <TableCell className="py-2">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-36">
                        <DropdownMenuItem className="gap-2 text-sm">
                          <Eye className="w-3.5 h-3.5" />
                          Перегляд
                        </DropdownMenuItem>
                        <DropdownMenuItem className="gap-2 text-sm">
                          <Edit2 className="w-3.5 h-3.5" />
                          Редагувати
                        </DropdownMenuItem>
                        <DropdownMenuItem className="gap-2 text-rose-600 text-sm">
                          <Trash2 className="w-3.5 h-3.5" />
                          Видалити
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-lg shadow-sm border border-slate-200 p-3 hover:shadow-md transition-shadow group"
            >
              <div className="aspect-[4/3] rounded bg-slate-100 flex items-center justify-center mb-2">
                <ImageIcon className="w-8 h-8 text-slate-300" />
              </div>
              <div className="space-y-1">
                <p className="text-[10px] text-slate-500">{product.sku}</p>
                <h3 className="font-semibold text-slate-900 text-sm truncate">{product.name}</h3>
                <Badge variant="secondary" className="bg-slate-100 text-slate-700 text-[10px] py-0">
                  {product.category}
                </Badge>
                <div className="flex items-center justify-between pt-1">
                  <span
                    className={cn(
                      'text-xs font-medium',
                      product.stock === 0 ? 'text-rose-600' : 'text-emerald-600'
                    )}
                  >
                    {product.stock} шт
                  </span>
                  <span className="font-bold text-slate-900 text-sm">{product.price} грн</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      <div className="flex items-center justify-between bg-white p-3 rounded-lg shadow-sm">
        <p className="text-xs text-slate-600">
          Всього <span className="font-medium text-slate-900">{filteredProducts.length}</span>{' '}
          товарів
        </p>
        <div className="flex items-center gap-1">
          <Button variant="outline" size="icon" className="h-7 w-7" disabled>
            <ChevronLeft className="w-3.5 h-3.5" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 min-w-[28px] px-2 text-xs bg-indigo-600 text-white hover:bg-indigo-700"
          >
            1
          </Button>
          <Button variant="outline" size="icon" className="h-7 w-7" disabled>
            <ChevronRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
