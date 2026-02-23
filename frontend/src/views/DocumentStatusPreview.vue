<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Статуси документів</h1>
        <p class="text-sm text-gray-500 mt-1">Огляд поточних статусів у системі (Дизайн-концепт)</p>
      </div>
      <div class="flex space-x-3">
        <el-button type="primary" class="shadow-sm font-semibold tracking-wide">
          Створити новий
        </el-button>
      </div>
    </div>

    <!-- Stats row -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 p-6 flex flex-col items-center justify-center transition-all hover:-translate-y-1 hover:shadow-[0_8px_20px_-6px_rgba(6,81,237,0.15)] relative overflow-hidden group">
        <div class="absolute inset-0 bg-blue-500 translate-y-[100%] group-hover:translate-y-[98%] transition-transform duration-300"></div>
        <div class="text-gray-400 text-sm font-medium mb-1 uppercase tracking-wider">DRAFT</div>
        <div class="text-4xl font-black text-gray-800 my-2">12</div>
        <div class="flex items-center text-xs text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full font-medium border border-blue-100">
          <span class="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></span>Очікують проведення
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 p-6 flex flex-col items-center justify-center transition-all hover:-translate-y-1 hover:shadow-[0_8px_20px_-6px_rgba(6,81,237,0.15)] relative overflow-hidden group">
        <div class="absolute inset-0 bg-green-500 translate-y-[100%] group-hover:translate-y-[98%] transition-transform duration-300"></div>
        <div class="text-gray-400 text-sm font-medium mb-1 uppercase tracking-wider">POSTED</div>
        <div class="text-4xl font-black text-gray-800 my-2">48</div>
        <div class="flex items-center text-xs text-green-600 bg-green-50 px-3 py-1.5 rounded-full font-medium border border-green-100">
          <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>Проведені успішно
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 p-6 flex flex-col items-center justify-center transition-all hover:-translate-y-1 hover:shadow-[0_8px_20px_-6px_rgba(6,81,237,0.15)] relative overflow-hidden group">
        <div class="absolute inset-0 bg-red-500 translate-y-[100%] group-hover:translate-y-[98%] transition-transform duration-300"></div>
        <div class="text-gray-400 text-sm font-medium mb-1 uppercase tracking-wider">CANCELLED</div>
        <div class="text-4xl font-black text-gray-800 my-2">3</div>
        <div class="flex items-center text-xs text-red-600 bg-red-50 px-3 py-1.5 rounded-full font-medium border border-red-100">
          <span class="w-1.5 h-1.5 bg-red-500 rounded-full mr-2"></span>Скасовані
        </div>
      </div>
      <div class="bg-gray-900 rounded-xl shadow-lg border border-gray-800 p-6 flex flex-col items-center justify-center relative overflow-hidden">
        <div class="absolute -right-10 -top-10 w-32 h-32 bg-blue-500/20 rounded-full blur-2xl"></div>
        <div class="text-gray-400 text-sm font-medium mb-1 uppercase tracking-wider">ТОТАЛ СУМА</div>
        <div class="text-4xl font-black text-white my-2">₴ 124K</div>
        <div class="text-xs text-gray-300 mt-1 uppercase tracking-widest opacity-80">Усі проведені</div>
      </div>
    </div>

    <!-- Main Content Area with Extension Zone -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      
      <!-- Core Table Area -->
      <div class="xl:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
          <h2 class="font-bold text-gray-800 text-lg">Останні документи</h2>
          <el-input placeholder="Пошук (Наприклад: INV-001)..." size="default" style="width: 280px" class="!rounded-lg" />
        </div>
        <div class="p-0 flex-1 overflow-x-auto">
          <table class="w-full text-left text-sm text-gray-600 whitespace-nowrap">
            <thead class="bg-gray-50/80 text-gray-500 text-xs uppercase tracking-wider">
              <tr>
                <th class="px-6 py-4 font-semibold">Документ</th>
                <th class="px-6 py-4 font-semibold">Дата</th>
                <th class="px-6 py-4 font-semibold">Контрагент</th>
                <th class="px-6 py-4 font-semibold">Сума</th>
                <th class="px-6 py-4 font-semibold text-right">Статус</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr class="hover:bg-blue-50/50 transition duration-150 cursor-pointer group">
                <td class="px-6 py-4">
                  <span class="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">INV-0012</span>
                </td>
                <td class="px-6 py-4 text-gray-500">Сьогодні, 14:30</td>
                <td class="px-6 py-4 font-medium text-gray-700">ТОВ "Ромашка"</td>
                <td class="px-6 py-4 font-semibold text-gray-900">₴ 12,500.00</td>
                <td class="px-6 py-4 text-right">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-green-100 text-green-700 border border-green-200">
                    <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>POSTED
                  </span>
                </td>
              </tr>
              <tr class="hover:bg-blue-50/50 transition duration-150 cursor-pointer group">
                <td class="px-6 py-4">
                  <span class="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">ORD-0099</span>
                </td>
                <td class="px-6 py-4 text-gray-500">Вчора, 09:15</td>
                <td class="px-6 py-4 font-medium text-gray-700">ФОП Шевченко</td>
                <td class="px-6 py-4 font-semibold text-gray-900">₴ 3,200.00</td>
                <td class="px-6 py-4 text-right">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200">
                    <span class="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></span>DRAFT
                  </span>
                </td>
              </tr>
              <tr class="hover:bg-blue-50/50 transition duration-150 cursor-pointer group">
                <td class="px-6 py-4">
                  <span class="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">PR-0005</span>
                </td>
                <td class="px-6 py-4 text-gray-500">21 Лют, 18:45</td>
                <td class="px-6 py-4 font-medium text-gray-700">ТОВ "СпецПостач"</td>
                <td class="px-6 py-4 font-semibold text-gray-900">₴ 45,000.00</td>
                <td class="px-6 py-4 text-right">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-gray-100 text-gray-700 border border-gray-200">
                    <span class="w-1.5 h-1.5 bg-gray-500 rounded-full mr-2"></span>CANCELLED
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Extension Zone -->
      <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl shadow-inner border border-indigo-100/60 p-6 flex flex-col relative overflow-hidden group">
        <!-- Decoration -->
        <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/40 rounded-full blur-3xl"></div>
        <div class="absolute -left-10 -bottom-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl"></div>

        <div class="relative z-10 flex items-center mb-5">
          <div class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center mr-4 shadow-lg shadow-indigo-200">
            <el-icon class="text-lg"><DataAnalysis /></el-icon>
          </div>
          <div>
            <h2 class="font-bold text-indigo-950 text-lg">Extension Zone</h2>
            <p class="text-xs text-indigo-600/80 uppercase tracking-widest font-semibold mt-0.5">Plug & Play UI</p>
          </div>
        </div>
        
        <div class="relative z-10 text-sm text-indigo-900/70 mb-8 leading-relaxed">
          Тут ядро системи (Core) реєструє хук: 
          <code class="block bg-white/80 border border-indigo-100 rounded text-xs px-2 py-1.5 mt-2 font-mono text-indigo-800 shadow-sm">&lt;ExtensionSlot name="sidebar" /&gt;</code>
          <br/>
          Якщо увімкнено плагін <strong class="text-indigo-800">Advanced Analytics</strong>, він ін'єктить сюди інтерактивну кругову діаграму або графік трендів. Якщо плагін вимкнено — ядро просто ховає цю колонку і таблиця розширюється на 100%.
        </div>

        <div class="relative z-10 mt-auto bg-white/70 backdrop-blur-md border px-4 py-8 rounded-xl flex flex-col items-center justify-center border-dashed border-indigo-300 text-indigo-500 hover:bg-white hover:text-indigo-600 transition-colors cursor-pointer group/btn">
          <div class="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center mb-3 group-hover/btn:scale-110 transition-transform">
            <el-icon class="text-2xl"><Plus /></el-icon>
          </div>
          <span class="text-sm font-semibold tracking-wide">Додати Розширення</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { DataAnalysis, Plus } from '@element-plus/icons-vue'
// Це лише візуальний макет. Для повної функціональності тут будуть реальні API виклики та <ExtensionSlot />.
</script>

<style scoped>
/* Scoped styles applied to not interfere with other files */
.el-input :deep(.el-input__wrapper) {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}
.el-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}
</style>
