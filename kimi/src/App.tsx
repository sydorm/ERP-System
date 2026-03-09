import { useState } from 'react';
import { Sidebar, type ViewType } from './sections/Sidebar';
import { Header } from './sections/Header';
import { StatsCards } from './sections/StatsCards';
import { ProductsTable } from './sections/ProductsTable';
import { ProductForm } from './sections/ProductForm';
import { CharacteristicsSettings } from './sections/CharacteristicsSettings';
import { SmartBOMCalculator } from './sections/SmartBOMCalculator';
import { PricingCalculator } from './sections/PricingCalculator';
import { ProductionPlanning } from './sections/ProductionPlanning';
import { SalesOrders } from './sections/SalesOrders';
import { Employees } from './sections/Employees';
import { Payroll } from './sections/Payroll';
import { PayrollTypes } from './sections/PayrollTypes';
import { Toaster } from '@/components/ui/sonner';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('products');

  const handleViewChange = (view: ViewType) => {
    setCurrentView(view);
  };

  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-xl font-bold text-slate-900">Головна панель</h2>
              <p className="text-sm text-slate-500">Огляд бізнесу</p>
            </div>
            <StatsCards />
          </div>
        );
      
      case 'products':
        return (
          <div className="space-y-4">
            <StatsCards />
            <ProductsTable />
          </div>
        );
      
      case 'product-create':
        return <ProductForm onCancel={() => setCurrentView('products')} onSave={() => setCurrentView('products')} />;
      
      case 'characteristics':
        return <CharacteristicsSettings onBack={() => setCurrentView('products')} />;
      
      case 'smart-bom':
        return <SmartBOMCalculator onBack={() => setCurrentView('products')} onSave={() => setCurrentView('products')} />;
      
      case 'pricing':
        return <PricingCalculator onBack={() => setCurrentView('products')} onSave={() => setCurrentView('products')} />;
      
      case 'warehouses':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Склади</h2>
            <p className="text-sm text-slate-500">Управління складами</p>
          </div>
        );
      
      case 'inventory':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Залишки</h2>
            <p className="text-sm text-slate-500">Облік запасів</p>
          </div>
        );
      
      case 'sales-orders':
        return <SalesOrders />;
      
      case 'customers':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Клієнти</h2>
            <p className="text-sm text-slate-500">База клієнтів</p>
          </div>
        );
      
      case 'purchase-orders':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Замовлення постачальникам</h2>
            <p className="text-sm text-slate-500">Управління закупівлями</p>
          </div>
        );
      
      case 'suppliers':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Постачальники</h2>
            <p className="text-sm text-slate-500">База постачальників</p>
          </div>
        );
      
      case 'production-planning':
        return <ProductionPlanning onBack={() => setCurrentView('dashboard')} />;
      
      case 'production-orders':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Виробничі замовлення</h2>
            <p className="text-sm text-slate-500">Список виробничих замовлень</p>
          </div>
        );
      
      case 'work-centers':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Робочі центри</h2>
            <p className="text-sm text-slate-500">Управління робочими центрами</p>
          </div>
        );
      
      case 'employees':
        return <Employees />;
      
      case 'payroll':
        return <Payroll />;
      
      case 'payroll-types':
        return <PayrollTypes />;
      
      case 'reports':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Звіти</h2>
            <p className="text-sm text-slate-500">Фінансові та виробничі звіти</p>
          </div>
        );
      
      case 'analytics':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Аналітика</h2>
            <p className="text-sm text-slate-500">Аналіз бізнес-показників</p>
          </div>
        );
      
      case 'company':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Компанія</h2>
            <p className="text-sm text-slate-500">Налаштування компанії</p>
          </div>
        );
      
      case 'users':
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-bold text-slate-900">Користувачі</h2>
            <p className="text-sm text-slate-500">Управління користувачами системи</p>
          </div>
        );
      
      default:
        return (
          <div className="space-y-4">
            <StatsCards />
            <ProductsTable />
          </div>
        );
    }
  };

  const getHeaderTitle = () => {
    const titles: Record<ViewType, string> = {
      dashboard: 'Головна панель',
      products: 'Номенклатура',
      'product-create': 'Новий товар',
      characteristics: 'Налаштування характеристик',
      'smart-bom': 'Розумна специфікація',
      pricing: 'Ціноутворення',
      warehouses: 'Склади',
      inventory: 'Залишки',
      'sales-orders': 'Замовлення покупців',
      customers: 'Клієнти',
      'purchase-orders': 'Замовлення постачальникам',
      suppliers: 'Постачальники',
      'production-planning': 'Планування виробництва',
      'production-orders': 'Виробничі замовлення',
      'work-centers': 'Робочі центри',
      employees: 'Співробітники',
      payroll: 'Нарахування ЗП',
      'payroll-types': 'Види нарахувань',
      reports: 'Звіти',
      analytics: 'Аналітика',
      settings: 'Налаштування',
      company: 'Компанія',
      users: 'Користувачі',
    };
    return titles[currentView] || 'ERP Pro';
  };

  const getBreadcrumbs = () => {
    const breadcrumbs: Record<ViewType, { label: string; view?: ViewType }[]> = {
      dashboard: [{ label: 'Головна' }],
      products: [{ label: 'Номенклатура' }],
      'product-create': [{ label: 'Номенклатура', view: 'products' }, { label: 'Новий товар' }],
      characteristics: [{ label: 'Номенклатура', view: 'products' }, { label: 'Характеристики' }],
      'smart-bom': [{ label: 'Номенклатура', view: 'products' }, { label: 'Специфікації BOM' }],
      pricing: [{ label: 'Номенклатура', view: 'products' }, { label: 'Ціноутворення' }],
      warehouses: [{ label: 'Склад' }, { label: 'Склади' }],
      inventory: [{ label: 'Склад' }, { label: 'Залишки' }],
      'sales-orders': [{ label: 'Продажі' }, { label: 'Замовлення' }],
      customers: [{ label: 'Продажі' }, { label: 'Клієнти' }],
      'purchase-orders': [{ label: 'Закупівлі' }, { label: 'Замовлення' }],
      suppliers: [{ label: 'Закупівлі' }, { label: 'Постачальники' }],
      'production-planning': [{ label: 'Виробництво' }, { label: 'Планування' }],
      'production-orders': [{ label: 'Виробництво' }, { label: 'Виробничі замовлення' }],
      'work-centers': [{ label: 'Виробництво' }, { label: 'Робочі центри' }],
      employees: [{ label: 'Персонал' }, { label: 'Співробітники' }],
      payroll: [{ label: 'Персонал' }, { label: 'Нарахування ЗП' }],
      'payroll-types': [{ label: 'Персонал' }, { label: 'Види нарахувань' }],
      reports: [{ label: 'Звіти та аналітика' }, { label: 'Звіти' }],
      analytics: [{ label: 'Звіти та аналітика' }, { label: 'Аналітика' }],
      settings: [{ label: 'Налаштування' }],
      company: [{ label: 'Налаштування' }, { label: 'Компанія' }],
      users: [{ label: 'Налаштування' }, { label: 'Користувачі' }],
    };
    return breadcrumbs[currentView] || [{ label: 'Головна' }];
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar */}
      <Sidebar currentView={currentView} onViewChange={handleViewChange} />

      {/* Main Content */}
      <div className="ml-56 min-h-screen flex flex-col">
        {/* Header */}
        <Header
          title={getHeaderTitle()}
          breadcrumbs={getBreadcrumbs().map(b => ({ 
            label: b.label, 
            href: b.view ? '#' : undefined,
            active: !b.view
          }))}
          onCreateClick={currentView === 'products' ? () => setCurrentView('product-create') : undefined}
        />

        {/* Content */}
        <main className="flex-1 p-4 overflow-auto">
          {renderContent()}
        </main>
      </div>

      {/* Toast notifications */}
      <Toaster position="top-right" />
    </div>
  );
}

export default App;
