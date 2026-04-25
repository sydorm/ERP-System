<template>
  <div class="erp-page-container">
    <div class="erp-toolbar">
      <div class="erp-toolbar-left">
        <el-button size="small" :icon="ArrowLeft" @click="goBack" class="erp-btn-icon" title="Назад" />
        <el-button type="warning" size="small" :loading="submitting" @click="saveOrder('post_close')" class="erp-btn-primary">
          Провести та закрити
        </el-button>
        <el-button size="small" @click="saveOrder('save')" class="erp-btn" :loading="submitting">Записати</el-button>
        <el-button size="small" @click="saveOrder('post')" class="erp-btn" :loading="submitting">Провести</el-button>
        <el-dropdown v-if="isEditMode" trigger="click" @command="handleCreateBasedOn" size="small">
          <el-button size="small" class="erp-btn">
            Створити на підставі <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="invoice">Видаткова накладна</el-dropdown-item>
              <el-dropdown-item command="payment">Вхідний платіж</el-dropdown-item>
              <el-dropdown-item command="purchase_order">Замовлення постачальнику</el-dropdown-item>
              <el-dropdown-item command="production_order" divided><el-icon><Tools /></el-icon> Завдання на виробництво</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <div class="erp-doc-info">
          <span class="erp-doc-title">{{ isEditMode ? 'Замовлення покупця ' + form.order_number : 'Замовлення покупця (створення)' }}</span>
        </div>
      </div>
      <div class="erp-toolbar-right">
        <el-button size="small" class="erp-btn-icon" :icon="isHeaderExpanded ? ArrowUp : ArrowDown" :title="isHeaderExpanded ? 'Згорнути шапку' : 'Розгорнути шапку'" @click="isHeaderExpanded = !isHeaderExpanded" />
        <el-button v-if="isEditMode" size="small" class="erp-btn-icon" :icon="Timer" title="Історія змін" @click="showAuditLog" />
        <el-dropdown trigger="click" size="small">
          <el-button size="small" class="erp-btn-icon" :icon="MoreFilled" title="Більше дій" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleCopyOrder"><el-icon><CopyDocument /></el-icon> Копіювати замовлення</el-dropdown-item>
              <el-dropdown-item @click="handlePrint"><el-icon><Printer /></el-icon> Друк</el-dropdown-item>
              <el-dropdown-item @click="handleSendEmail" :disabled="!selectedCustomerObj"><el-icon><Promotion /></el-icon> Надіслати email</el-dropdown-item>
              <el-dropdown-item @click="handleExportExcel"><el-icon><Download /></el-icon> Експорт в Excel</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- Order header fields -->
    <el-collapse-transition>
      <div class="erp-header-fields" v-show="isHeaderExpanded">
      <div class="erp-field-row justify-between">
        <div class="erp-field">
          <span class="erp-label">Номер:</span>
          <el-input v-model="form.order_number" size="small" class="erp-input-wrapper" disabled style="width:120px" />
        </div>
        <div class="erp-field">
          <span class="erp-label">від:</span>
          <el-date-picker v-model="form.order_date" type="date" size="small" class="erp-input-wrapper" value-format="YYYY-MM-DD" style="width:145px" />
        </div>
        <div class="erp-field">
          <span class="erp-label">Відвантаження:</span>
          <el-date-picker v-model="form.shipping_date" type="date" size="small" class="erp-input-wrapper" value-format="YYYY-MM-DD" placeholder="Планова" style="width:145px" />
        </div>
        <div class="erp-badges-group ml-auto flex gap-2">
            <el-select v-model="form.status" size="small" class="erp-status-select" :class="statusType" style="width:140px">
              <el-option v-for="s in orderStatuses" :key="s.code" :label="s.name" :value="s.code">
                <span class="flex items-center gap-2">
                   <span class="w-2 h-2 rounded-full" :style="{backgroundColor: s.color || '#ccc'}"></span>
                   {{ s.name }}
                </span>
              </el-option>
            </el-select>
            <div class="payment-status-badge" :class="paymentStatusClass" style="margin-top:0">{{ paymentStatusLabel }}</div>
        </div>
      </div>
      <div class="erp-field-row mt-1">
        <div class="erp-field client-field">
          <span class="erp-label req">Покупець:</span>
          <el-select v-model="form.counterparty_id" filterable size="small" class="erp-input-wrapper client-select" @change="onClientChange">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
      </div>
      <div class="client-info-banner" v-if="selectedCustomerObj">
        <span class="client-info-item"><el-icon><Phone /></el-icon> {{ selectedCustomerObj.phone || '—' }}</span>
        <span class="client-info-item"><el-icon><Message /></el-icon> {{ selectedCustomerObj.email || '—' }}</span>
        <span class="client-info-item"><el-icon><Location /></el-icon> {{ selectedCustomerObj.address || '—' }}</span>
        <span class="client-info-badge" v-if="selectedCustomerObj.credit_limit">
          Кредитний ліміт: {{ formatCurrency(selectedCustomerObj.credit_limit) }}
        </span>
      </div>
    </div>
    </el-collapse-transition>

    <!-- Main body: tabs + sidebar -->
    <div class="order-body">
      <div class="order-main">
        <el-tabs v-model="activeTab" class="order-tabs">

          <!-- TAB: Товари -->
          <el-tab-pane name="items">
            <template #label><el-icon><Box /></el-icon>&nbsp;Товари <el-badge v-if="form.lines.length" :value="form.lines.length" class="tab-badge" /></template>
            <div class="tab-toolbar">
              <el-button size="small" class="erp-btn" @click="addLine">Додати</el-button>
              <el-button size="small" class="erp-btn" :icon="Search" @click="openNomenclatureDialog(form.lines.length - 1 || 0)">Підібрати</el-button>
              <el-button size="small" class="erp-btn-icon" :icon="Setting" title="Налаштування колонок" />
              <div class="tab-toolbar-right">
                <span class="erp-label">Склад:</span>
                <el-select v-model="form.warehouse_id" size="small" class="warehouse-select">
                  <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
                </el-select>
              </div>
            </div>
            <div class="erp-table-wrapper" v-loading="loading">
              <el-table :data="form.lines" border size="small" class="erp-dense-table" height="100%">
                <el-table-column type="index" label="N" width="40" align="center" />
                <el-table-column label="Номенклатура" min-width="200">
                  <template #default="scope">
                    <el-select v-model="scope.row.product_id" filterable size="small" placeholder="" class="erp-cell-input" @change="(val) => handleProductChange(val, scope.row)">
                      <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="Характеристика" min-width="140" v-if="visibleCols.characteristic">
                  <template #default="scope">
                    <div class="erp-cell-trigger" @click="openVariantSelector(scope.row)">
                      <span class="selection-text" v-if="scope.row.variant_id">{{ getVariantLabelByLine(scope.row) }}</span>
                      <span class="selection-text virtual" v-else-if="scope.row._virtual_label">{{ scope.row._virtual_label }}</span>
                      <span class="placeholder" v-else>...</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="К-ть" width="110">
                  <template #default="scope">
                    <el-input-number size="small" v-model="scope.row.quantity" :min="0.001" :step="0.001" :precision="3" @change="updateLineTotal(scope.row)" class="erp-cell-input num" style="width:100%" />
                  </template>
                </el-table-column>
                <el-table-column label="Резерв" width="70" align="center">
                  <template #default><el-checkbox /></template>
                </el-table-column>
                <el-table-column label="Ціна" width="120">
                  <template #default="scope">
                    <el-input-number size="small" v-model="scope.row.price" :min="0" :precision="2" @change="updateLineTotal(scope.row)" class="erp-cell-input num" style="width:100%" />
                  </template>
                </el-table-column>

                <el-table-column label="Сума" width="130">
                  <template #default="scope">
                    <el-input-number size="small" v-model="scope.row.total" :min="0" :precision="2" @change="updateLinePrice(scope.row)" class="erp-cell-input num" style="width:100%" />
                  </template>
                </el-table-column>
                <el-table-column label="Специфікація" min-width="120">
                  <template #default="scope">
                    <el-select v-model="scope.row.specification_id" size="small" placeholder="За замовчуванням" clearable class="erp-cell-input" style="width:100%">
                      <el-option v-for="s in (specsCache[scope.row.product_id] || [])" :key="s.id" :label="s.is_default ? s.name + ' (Авто)' : s.name" :value="s.id" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="" width="40" align="center" fixed="right">
                  <template #default="scope">
                    <el-button type="danger" :icon="Delete" link size="small" @click="removeLine(scope.$index)" style="padding:0;height:auto;" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="items-comment">
              <el-input v-model="form.comment" type="textarea" :autosize="{ minRows: 2, maxRows: 3 }" placeholder="Коментар..." class="erp-comment-input" />
            </div>
          </el-tab-pane>

          <!-- TAB: Доставка -->
          <el-tab-pane name="delivery">
            <template #label><el-icon><Van /></el-icon>&nbsp;Доставка</template>
            <div class="tab-content-card">
              <div class="fields-grid-3">
                <div class="field-block">
                  <label class="field-label">Спосіб доставки</label>
                  <el-select v-model="delivery.method" size="small" style="width:100%">
                    <el-option value="self" label="Самовивіз" /><el-option value="courier" label="Кур'єр" />
                    <el-option value="np_branch" label="Нова Пошта (відділення)" /><el-option value="np_courier" label="Нова Пошта (кур'єр)" />
                    <el-option value="truck" label="Вантажний транспорт" />
                  </el-select>
                </div>
                <div class="field-block">
                  <label class="field-label">Бажана дата</label>
                  <el-date-picker v-model="delivery.desired_date" type="date" size="small" value-format="YYYY-MM-DD" style="width:100%" />
                </div>
                <div class="field-block">
                  <label class="field-label">Вартість доставки (₴)</label>
                  <el-input-number v-model="delivery.cost" :min="0" :precision="2" :controls="false" size="small" style="width:100%" />
                </div>
              </div>
              <div class="fields-grid-2">
                <div class="field-block">
                  <label class="field-label">Отримувач</label>
                  <el-input v-model="delivery.recipient_name" size="small" placeholder="ПІБ отримувача" />
                </div>
                <div class="field-block">
                  <label class="field-label">Телефон отримувача</label>
                  <el-input v-model="delivery.recipient_phone" size="small" placeholder="+380..." />
                </div>
              </div>
              <div class="field-block">
                <label class="field-label">Адреса доставки</label>
                <el-input v-model="delivery.address" type="textarea" :autosize="{ minRows: 2 }" size="small" placeholder="Повна адреса..." />
              </div>
              <div class="field-block" v-if="delivery.method === 'np_branch'">
                <label class="field-label">Номер відділення НП</label>
                <el-input v-model="delivery.branch_number" size="small" placeholder="№ відділення" style="width:160px" />
              </div>
            </div>
          </el-tab-pane>

          <!-- TAB: Оплата -->
          <el-tab-pane name="payment">
            <template #label><el-icon><CreditCard /></el-icon>&nbsp;Оплата</template>
            <div class="tab-content-card">
              <div class="fields-grid-3">
                <div class="field-block">
                  <label class="field-label">Спосіб оплати</label>
                  <el-select v-model="payment.method" size="small" style="width:100%">
                    <el-option value="cash" label="Готівка" /><el-option value="card" label="Картка" />
                    <el-option value="bank_transfer" label="Банківський переказ" /><el-option value="credit" label="В кредит" />
                    <el-option value="installment" label="Розстрочка" />
                  </el-select>
                </div>
                <div class="field-block">
                  <label class="field-label">Оплатити до</label>
                  <el-date-picker v-model="payment.due_date" type="date" size="small" value-format="YYYY-MM-DD" style="width:100%" />
                </div>
                <div class="field-block">
                  <label class="field-label">Статус оплати</label>
                  <div class="payment-status-badge" :class="paymentStatusClass">{{ paymentStatusLabel }}</div>
                </div>
              </div>
              <div class="payment-summary-box">
                <div class="ps-row"><span>Сума замовлення:</span><span>{{ formatCurrency(totalAmount) }}</span></div>
                <div class="ps-row"><span>Доставка:</span><span>{{ formatCurrency(delivery.cost) }}</span></div>
                <div class="ps-divider"></div>
                <div class="ps-row ps-row--bold"><span>Всього до оплати:</span><span>{{ formatCurrency(totalAmount + delivery.cost) }}</span></div>
                <div class="ps-divider"></div>
                <div class="ps-row"><span>Сплачено:</span><span class="text-green">{{ formatCurrency(paidAmount) }}</span></div>
                <div class="ps-row"><span>Залишок:</span><span :class="remainingAmount > 0 ? 'text-red' : 'text-green'">{{ formatCurrency(remainingAmount) }}</span></div>
              </div>
              <div v-if="payment.records.length > 0" class="payments-list">
                <div class="payments-list-title">Історія платежів</div>
                <el-table :data="payment.records" size="small" border>
                  <el-table-column prop="date" label="Дата" width="110" />
                  <el-table-column prop="method_label" label="Спосіб" />
                  <el-table-column label="Сума" align="right" width="120">
                    <template #default="s">{{ formatCurrency(s.row.amount) }}</template>
                  </el-table-column>
                  <el-table-column label="Статус" width="110" align="center">
                    <template #default="s">
                      <el-tag size="small" :type="s.row.status === 'completed' ? 'success' : 'warning'">
                        {{ s.row.status === 'completed' ? 'Виконано' : 'Очікує' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <el-button v-if="remainingAmount > 0" size="small" class="erp-btn" :icon="Plus" @click="showAddPaymentDialog = true" style="margin-top:12px">Додати платіж</el-button>
            </div>
          </el-tab-pane>

          <!-- TAB: Документи -->
          <el-tab-pane name="documents">
            <template #label><el-icon><Document /></el-icon>&nbsp;Документи <el-badge v-if="orderDocs.length" :value="orderDocs.length" class="tab-badge" /></template>
            <div class="tab-content-card">
              <div class="docs-actions">
                <el-button size="small" class="erp-btn" :icon="Document" @click="createInvoice">Рахунок</el-button>
                <el-button size="small" class="erp-btn" :icon="Van" @click="createWaybill">Накладна</el-button>
              </div>
              <div v-if="orderDocs.length === 0" class="empty-state">
                <el-icon size="40" color="#cbd5e1"><Document /></el-icon>
                <p>Документи ще не створені</p>
              </div>
              <div v-else class="docs-list">
                <div v-for="doc in orderDocs" :key="doc.id" class="doc-item">
                  <el-icon size="24" :color="doc.type === 'invoice' ? '#10b981' : '#f59e0b'">
                    <component :is="doc.type === 'invoice' ? Document : Van" />
                  </el-icon>
                  <div class="doc-info">
                    <span class="doc-name">{{ doc.type === 'invoice' ? 'Рахунок на оплату' : 'Накладна' }}</span>
                    <span class="doc-meta">№ {{ doc.number }} від {{ doc.date }}</span>
                  </div>
                  <el-tag size="small" :type="doc.status === 'issued' ? 'primary' : 'info'">{{ doc.status === 'issued' ? 'Виписано' : 'Чернетка' }}</el-tag>
                  <el-button size="small" :icon="View" circle class="erp-btn-icon" />
                  <el-button size="small" :icon="Printer" circle class="erp-btn-icon" />
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane name="bom">
            <template #label><el-icon><List /></el-icon>&nbsp;Специфікація <el-badge v-if="orderBOM.length" :value="orderBOM.length" class="tab-badge" /></template>
            <div class="tab-content-card print-area" style="background-color: #f9fafb; padding: 20px;">
              <div v-if="orderBOM.length === 0" class="empty-state">
                <el-icon size="40" color="#cbd5e1"><List /></el-icon>
                <p>Додайте товари з налаштованою специфікацією, щоб побачити розрахунок матеріалів</p>
              </div>
              <div v-else class="bom-document">
                <div class="bom-doc-actions no-print">
                  <el-button type="primary" :icon="Printer" size="small" @click="printBOM">Друк специфікації</el-button>
                </div>
                <div class="bom-doc-header">
                  <div class="bom-doc-title">Специфікація матеріалів</div>
                  <div class="bom-doc-meta">
                    <div><strong>Замовлення:</strong> {{ form.order_number }} від {{ form.order_date }}</div>
                    <div><strong>Клієнт:</strong> {{ selectedCustomerObj ? selectedCustomerObj.name : '—' }}</div>
                  </div>
                </div>
                <div class="bom-table-wrapper">
                  <table class="bom-print-table">
                    <thead>
                      <tr>
                        <th width="15%">Артикул</th>
                        <th width="35%">Матеріал / Компонент</th>
                        <th width="30%">Для яких товарів</th>
                        <th width="20%" class="text-right">Потрібно</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, i) in orderBOM" :key="i">
                        <td>{{ row.component_sku }}</td>
                        <td class="font-medium">{{ row.component_name }}</td>
                        <td>
                          <div v-for="(src, idx) in row.sourceLines" :key="idx" class="text-xs text-gray-600 mb-1">
                            {{ src.productName }} <span class="text-gray-400">({{ Number(src.qty).toFixed(4) }} {{ row.unit }})</span>
                          </div>
                        </td>
                        <td class="text-right font-bold text-blue-800">
                          {{ Number(row.totalQuantity).toFixed(4) }} <span class="text-xs text-gray-500 font-normal">{{ row.unit }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="bom-doc-footer mt-8 pt-4 border-t text-sm text-gray-500 flex justify-between">
                  <div>Сформовано автоматично ERP-системою</div>
                  <div>Всього унікальних матеріалів: {{ orderBOM.length }}</div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- TAB: Виробництво -->
          <el-tab-pane name="production">
            <template #label><el-icon><Tools /></el-icon>&nbsp;Виробництво</template>
            <div class="tab-content-card empty-state">
              <el-icon size="40" color="#cbd5e1"><Tools /></el-icon>
              <p>Виробничі завдання (в розробці)</p>
            </div>
          </el-tab-pane>

          <!-- TAB: Історія -->
          <el-tab-pane name="history">
            <template #label><el-icon><Timer /></el-icon>&nbsp;Історія</template>
            <div class="tab-content-card" style="padding:0">
              <div v-if="!isEditMode" class="empty-state"><p>Збережіть замовлення щоб бачити історію</p></div>
              <AuditLogViewer v-else v-model="auditLogVisible" entity-type="order" :entity-id="route.params.id" :inline="true" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- RIGHT: sidebar -->
      <div class="order-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-title">Підсумки замовлення</div>
          <div class="summary-rows">
            <div class="sum-row"><span>Позицій:</span><span>{{ form.lines.length }}</span></div>
            <div class="sum-row"><span>К-ть товарів:</span><span>{{ totalQty }} шт</span></div>
            <div class="sum-row"><span>Знижка:</span><span class="text-red">-{{ formatCurrency(discountAmount) }}</span></div>
            <div class="sum-row"><span>Доставка:</span><span>{{ formatCurrency(delivery.cost) }}</span></div>
            <div class="sum-divider"></div>
            <div class="sum-row"><span>Сума без ПДВ:</span><span>{{ formatCurrency(subtotal - vatTotal) }}</span></div>
            <div class="sum-row"><span>ПДВ (20%):</span><span>{{ formatCurrency(vatTotal) }}</span></div>
            <div class="sum-divider"></div>
            <div class="sum-row sum-row--total"><span>ВСЬОГО:</span><span class="total-value">{{ formatCurrency(totalAmount + delivery.cost) }}</span></div>
          </div>
          <div class="discount-field">
            <span>Знижка %:</span>
            <el-input-number v-model="form.discount_percent" :min="0" :max="100" :precision="1" :controls="false" size="small" style="width:70px" />
          </div>
        </div>
        <div class="sidebar-card">
          <div class="sidebar-card-title">Швидкі дії</div>
          <div class="quick-actions">
            <el-button size="small" class="qa-btn" @click="activeTab = 'delivery'"><el-icon><Van /></el-icon> Заповнити доставку</el-button>
            <el-button size="small" class="qa-btn" @click="createInvoice"><el-icon><Document /></el-icon> Виставити рахунок</el-button>
            <el-button size="small" class="qa-btn" @click="handlePrint"><el-icon><Printer /></el-icon> Друк замовлення</el-button>
            <el-button size="small" class="qa-btn" @click="handleSendEmail" :disabled="!selectedCustomerObj"><el-icon><Promotion /></el-icon> Надіслати клієнту</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialogs -->
    <el-dialog v-model="nomenclatureDialogVisible" title="Вибір номенклатури" width="800px" destroy-on-close>
      <el-input v-model="nomenclatureSearch" placeholder="Пошук..." :prefix-icon="Search" clearable style="margin-bottom:16px" />
      <el-table :data="filteredProducts" border height="400px" highlight-current-row @current-change="onDialogProductSelect">
        <el-table-column property="sku" label="SKU" width="120" />
        <el-table-column property="name" label="Назва" min-width="250" />
        <el-table-column property="category" label="Категорія" width="150" />
        <el-table-column label="Ціна" width="120" align="right">
          <template #default="scope">{{ formatShort(scope.row.price) }}</template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="nomenclatureDialogVisible = false">Скасувати</el-button>
        <el-button type="primary" :disabled="!selectedDialogProduct" @click="confirmDialogSelection">Вибрати</el-button>
      </template>
    </el-dialog>

    <VariantSelectorDialog v-model="variantSelectorVisible" :product="selectedProductForSelector" @select="onVariantSelected" @clear="clearVirtualVariant(activeLineForSelector)" />
    <AuditLogViewer v-if="isEditMode" v-model="auditLogVisible" entity-type="order" :entity-id="route.params.id" />

    <el-dialog v-model="showAddPaymentDialog" title="Додати платіж" width="380px">
      <el-form label-width="130px" size="small">
        <el-form-item label="Сума платежу">
          <el-input-number v-model="newPaymentAmount" :min="0" :max="remainingAmount" :precision="2" :controls="false" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPaymentDialog = false">Скасувати</el-button>
        <el-button type="primary" @click="addPayment">Додати</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, Search, Setting, ArrowDown, ArrowUp, Timer, MoreFilled, CopyDocument, Printer, Promotion, Download, Phone, Message, Location, Box, Van, CreditCard, Document, Tools, View, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { getProductSpecifications } from '@/api/specifications'
import VariantSelectorDialog from './VariantSelectorDialog.vue'
import AuditLogViewer from '@/components/AuditLogViewer.vue'

const route = useRoute()
const router = useRouter()

const handleCreateBasedOn = (command) => {
  const orderId = route.params.id;
  if (!orderId) return;

  if (command === 'invoice') {
    // router.push({ path: '/sales/invoices/new', query: { based_on: orderId } })
    ElMessage.info('Створення Видаткової накладної (в розробці)')
  } else if (command === 'payment') {
    // router.push({ path: '/finance/payments/new', query: { based_on: orderId, type: 'incoming' } })
    ElMessage.info('Створення Вхідного платежу (в розробці)')
  } else if (command === 'purchase_order') {
    // router.push({ path: '/purchases/orders/new', query: { based_on: orderId } })
    ElMessage.info('Створення Замовлення постачальнику (в розробці)')
  } else if (command === 'production_order') {
    router.push({ path: '/production/orders/new', query: { base_order: orderId } })
  }
}


// State
const loading = ref(false)
const submitting = ref(false)
const isEditMode = computed(() => !!route.params.id)
const activeTab = ref('items')
const isHeaderExpanded = ref(true)

// Delivery state
const delivery = reactive({
  method: 'self',
  desired_date: null,
  cost: 0,
  recipient_name: '',
  recipient_phone: '',
  address: '',
  branch_number: ''
})

// Payment state
const payment = reactive({
  method: 'bank_transfer',
  due_date: null,
  records: []
})
const showAddPaymentDialog = ref(false)
const newPaymentAmount = ref(0)

// Documents state
const orderDocs = ref([])

const form = reactive({
  order_number: 'Авто',
  order_date: new Date().toISOString().split('T')[0],
  shipping_date: null,
  counterparty_id: '',
  warehouse_id: '',
  contract: '',
  comment: '',
  discount_percent: 0,
  status: 'draft',
  lead_source: null,
  lines: []
})

const orderStatuses = ref([])
const leadSources = ref([])

// Column Visibility
const visibleCols = reactive({
  characteristic: true,
  discount: true
})

// Options
const customers = ref([])
const warehouses = ref([])
const products = ref([])

// Nomenclature Dialog State
const nomenclatureDialogVisible = ref(false)
const nomenclatureSearch = ref('')
const activeLineIndex = ref(-1)
const selectedDialogProduct = ref(null)

// Variant Selector State
const variantSelectorVisible = ref(false)
const selectedProductForSelector = ref(null)
const activeLineForSelector = ref(null)

// Specs and BOM State
const specsCache = ref({})

// Audit Log State
const auditLogVisible = ref(false)
const showAuditLog = () => {
  auditLogVisible.value = true
}

// Computed
const subtotal = computed(() => {
  return form.lines.reduce((acc, line) => acc + (line.total || 0), 0)
})

const calculateQuantity = (item, baseDimensions, variantValues) => {
  if (!item.is_calculated) return item.quantity

  const dims = {
    W: parseFloat(baseDimensions?.width_cm) || 0,
    H: parseFloat(baseDimensions?.height_cm) || 0,
    L: parseFloat(baseDimensions?.length_cm) || 0,
    Kg: parseFloat(baseDimensions?.weight_kg) || 0
  }

  if (variantValues && variantValues.length > 0) {
    variantValues.forEach(v => {
      const mapping = v.attribute?.mapped_dimension
      if (mapping === 'width_cm') dims.W = parseFloat(v.text_value) || parseFloat(v.option?.value) || dims.W
      if (mapping === 'height_cm') dims.H = parseFloat(v.text_value) || parseFloat(v.option?.value) || dims.H
      if (mapping === 'length_cm') dims.L = parseFloat(v.text_value) || parseFloat(v.option?.value) || dims.L
    })
  }

  // Apply calc_dim_config: use 'default' as fallback and 'char_name' to read from characteristics
  if (item.calc_dim_config) {
    const dimKeyMap = { h: 'H', w: 'W', l: 'L' }
    for (const [key, dimKey] of Object.entries(dimKeyMap)) {
      const cfg = item.calc_dim_config[key]
      if (!cfg) continue
      // Apply standard default if current dim is 0 and default is set
      if (dims[dimKey] === 0 && cfg.default > 0) {
        dims[dimKey] = cfg.default
      }
      // Override with characteristic value if char_name is specified
      if (cfg.char_name && variantValues?.length > 0) {
        const charNameLower = cfg.char_name.toLowerCase().trim()
        const found = variantValues.find(v => {
          const attrName = (v.attribute?.name || v.attribute?.slug || '').toLowerCase().trim()
          return attrName === charNameLower
        })
        if (found) {
          const val = parseFloat(found.text_value) || parseFloat(found.option?.value) || parseFloat(found.option?.label) || null
          if (val !== null && val > 0) dims[dimKey] = val
        }
      }
    }
  }

  let result = 0
  if (item.calc_type === 'interpolation') {
    const dp = item.calc_data_points

    // Normalize to per-dim format { h:[{x,qty}], w:[...], l:[...] }
    let normalized = null
    if (dp && !Array.isArray(dp) && dp.h !== undefined) {
      // Already new per-dim format
      normalized = dp
    } else if (Array.isArray(dp) && dp.length > 0 && dp[0].size_cm !== undefined) {
      // Old flat array [{size_cm, h, w, l}] → convert
      normalized = { h: [], w: [], l: [] }
      for (const pt of dp) {
        if (pt.h != null) normalized.h.push({ x: pt.size_cm || 0, qty: pt.h })
        if (pt.w != null) normalized.w.push({ x: pt.size_cm || 0, qty: pt.w })
        if (pt.l != null) normalized.l.push({ x: pt.size_cm || 0, qty: pt.l })
      }
    } else if (dp && !Array.isArray(dp) && (dp.height_cm || dp.width_cm || dp.length_cm)) {
      // Very old {height_cm:[{input,output}]...} format
      normalized = {
        h: (dp.height_cm || []).map(p => ({ x: p.input || 0, qty: p.output || 0 })),
        w: (dp.width_cm  || []).map(p => ({ x: p.input || 0, qty: p.output || 0 })),
        l: (dp.length_cm || []).map(p => ({ x: p.input || 0, qty: p.output || 0 })),
      }
    }

    if (!normalized) return item.quantity

    const dimKeyMap = { h: 'H', w: 'W', l: 'L' }
    let total = 0
    let hasAny = false

    for (const [key, dimKey] of Object.entries(dimKeyMap)) {
      const pts = (normalized[key] || []).filter(p => p.qty != null)
      if (!pts.length) continue
      hasAny = true
      const dimVal = dims[dimKey] || 0
      const sorted = [...pts].sort((a, b) => (a.x || 0) - (b.x || 0))
      const interp = (p1, p2, val) => {
        const slope = (p2.x !== p1.x) ? (p2.qty - p1.qty) / (p2.x - p1.x) : 0
        return p1.qty + slope * (val - p1.x)
      }
      let r = 0
      if (sorted.length === 1) { r = sorted[0].qty }
      else if (dimVal <= sorted[0].x) { r = interp(sorted[0], sorted[1], dimVal) }
      else if (dimVal >= sorted[sorted.length - 1].x) { r = interp(sorted[sorted.length - 2], sorted[sorted.length - 1], dimVal) }
      else {
        for (let i = 0; i < sorted.length - 1; i++) {
          if (dimVal >= sorted[i].x && dimVal <= sorted[i + 1].x) { r = interp(sorted[i], sorted[i + 1], dimVal); break }
        }
      }
      total += Math.max(0, r)
    }
    result = hasAny ? total : item.quantity
  }
  else if (item.calc_type === 'proportional') {
    const dimVal = dims[item.calc_dimension === 'width_cm' ? 'W' : (item.calc_dimension === 'height_cm' ? 'H' : 'L')] || 0
    const coeff = parseFloat(item.calc_formula) || 0
    result = dimVal * coeff
  }
  else if (item.calc_type === 'area') {
    result = dims.W * dims.H / 10000
  }
  else if (item.calc_type === 'volume') {
    result = dims.W * dims.H * dims.L / 1000000
  }
  else if (item.calc_type === 'formula') {
    try {
      const { W, H, L, Kg } = dims
      result = eval(item.calc_formula)
    } catch (e) {
      result = 0
    }
  }

  if (item.calc_waste_factor) {
    result *= (1 + parseFloat(item.calc_waste_factor))
  }
  return result
}

const orderBOM = computed(() => {
  const bom = []
  
  form.lines.forEach(line => {
    if (!line.product_id || !line.quantity) return
    const specs = specsCache.value[line.product_id] || []
    if (!specs.length) return
    
    // Use selected specification or fallback to default
    const spec = line.specification_id ? specs.find(s => s.id === line.specification_id) : (specs.find(s => s.is_default) || specs[0])
    if (!spec || !spec.items) return
    
    const product = products.value.find(p => p.id === line.product_id)
    
    let variantValues = []
    if (line.variant_id && product?.variants) {
       const variant = product.variants.find(v => v.id === line.variant_id)
       if (variant) variantValues = variant.values || []
    } else if (line._virtual_values) {
       variantValues = line._virtual_values
    }

    spec.items.forEach(item => {
      const qtyPerUnit = parseFloat(calculateQuantity(item, product, variantValues)) || 0
      if (qtyPerUnit <= 0) return
      
      const totalQty = qtyPerUnit * line.quantity
      const existing = bom.find(b => b.component_id === item.component_id)
      
      if (existing) {
        existing.totalQuantity += totalQty
        existing.sourceLines.push({ productName: product?.name, qty: totalQty })
      } else {
        bom.push({
          component_id: item.component_id,
          component_name: item.component?.name || 'Unknown',
          component_sku: item.component?.sku || '',
          unit: item.unit_of_measure,
          totalQuantity: totalQty,
          sourceLines: [{ productName: product?.name, qty: totalQty }]
        })
      }
    })
  })
  return bom
})

const discountAmount = computed(() => {
  return subtotal.value * (form.discount_percent || 0) / 100
})

const totalAmount = computed(() => {
  return subtotal.value - discountAmount.value
})

const filteredProducts = computed(() => {
  if (!nomenclatureSearch.value) return products.value
  const s = nomenclatureSearch.value.toLowerCase()
  return products.value.filter(p =>
    p.name.toLowerCase().includes(s) ||
    p.sku.toLowerCase().includes(s)
  )
})

const statusType = computed(() => {
  const status = orderStatuses.value.find(s => s.code === form.status)
  const color = status?.color || 'info'
  const validTypes = ['primary', 'success', 'info', 'warning', 'danger']
  return validTypes.includes(color) ? color : 'info'
})

// New computed properties
const selectedCustomerObj = computed(() => customers.value.find(c => c.id === form.counterparty_id) || null)

const totalQty = computed(() => form.lines.reduce((sum, l) => sum + (l.quantity || 0), 0))

const vatTotal = computed(() => form.lines.reduce((sum, l) => sum + ((l.total || 0) * 0.2), 0))

const paidAmount = computed(() => payment.records.filter(r => r.status === 'completed').reduce((sum, r) => sum + r.amount, 0))

const remainingAmount = computed(() => Math.max(0, totalAmount.value + delivery.cost - paidAmount.value))

const paymentStatusClass = computed(() => {
  if (remainingAmount.value <= 0) return 'ps-badge--green'
  if (paidAmount.value > 0) return 'ps-badge--amber'
  return 'ps-badge--red'
})

const paymentStatusLabel = computed(() => {
  if (remainingAmount.value <= 0) return 'Оплачено повністю'
  if (paidAmount.value > 0) return 'Частково оплачено'
  return 'Не оплачено'
})

const statusColor = computed(() => {
  const status = orderStatuses.value.find(s => s.code === form.status)
  const c = status?.color || 'gray'
  // Map our basic element colors to actual hex codes for dynamic display if they used standard names
  const colorMap = {
    gray: '#64748b',
    info: '#64748b',
    blue: '#3b82f6',
    primary: '#3b82f6',
    green: '#10b981',
    success: '#10b981',
    orange: '#f59e0b',
    warning: '#f59e0b',
    red: '#ef4444',
    danger: '#ef4444'
  }
  return status?.color || 'gray' // Return the raw color name/hex
})

const statusLabel = computed(() => {
  const status = orderStatuses.value.find(s => s.code === form.status)
  return status?.name || form.status
})

const goBack = () => router.push('/sales/orders')

// New action handlers
const handleCopyOrder = () => ElMessage.info('Копіювання замовлення (в розробці)')
const handlePrint = () => ElMessage.info('Друк замовлення (в розробці)')
const printBOM = () => {
  window.print()
}

const handleSendEmail = () => {
  const c = selectedCustomerObj.value
  if (!c?.email) { ElMessage.warning('У клієнта не вказано email'); return }
  ElMessage.success(`Email надіслано на ${c.email}`)
}
const handleExportExcel = () => ElMessage.info('Експорт в Excel (в розробці)')

const createInvoice = () => {
  const num = `РХ-${form.order_number || Date.now()}`
  orderDocs.value.push({ id: Date.now(), type: 'invoice', number: num, date: new Date().toISOString().split('T')[0], status: 'issued' })
  activeTab.value = 'documents'
  ElMessage.success(`Рахунок ${num} створено`)
}

const createWaybill = () => {
  const num = `НВ-${form.order_number || Date.now()}`
  orderDocs.value.push({ id: Date.now(), type: 'waybill', number: num, date: new Date().toISOString().split('T')[0], status: 'draft' })
  activeTab.value = 'documents'
  ElMessage.success(`Накладна ${num} створена`)
}

const addPayment = () => {
  if (!newPaymentAmount.value || newPaymentAmount.value <= 0) { ElMessage.error('Введіть суму'); return }
  const methodLabels = { cash: 'Готівка', card: 'Картка', bank_transfer: 'Банківський переказ', credit: 'В кредит', installment: 'Розстрочка' }
  payment.records.push({
    id: Date.now(), date: new Date().toISOString().split('T')[0],
    amount: newPaymentAmount.value, method_label: methodLabels[payment.method] || payment.method, status: 'completed'
  })
  ElMessage.success(`Платіж ${formatCurrency(newPaymentAmount.value)} додано`)
  newPaymentAmount.value = 0
  showAddPaymentDialog.value = false
}

const onClientChange = (clientId) => {
  const client = customers.value.find(c => c.id === clientId)
  // Auto-fill delivery info from client
  if (client) {
    if (client.address && !delivery.address) delivery.address = client.address
    if (client.phone && !delivery.recipient_phone) delivery.recipient_phone = client.phone
    if (client.name && !delivery.recipient_name) delivery.recipient_name = client.name
  }
  if (client && client.default_contract) {
    form.contract = client.default_contract
  }
}

const addLine = () => {
  form.lines.push({
    product_id: '',
    variant_id: null,
    specification_id: null,
    quantity: 1,
    price: 0,
    total: 0
  })
}

const removeLine = (index) => {
  form.lines.splice(index, 1)
}

const updateLineTotal = (line) => {
  line.total = parseFloat((line.quantity * line.price).toFixed(2))
}

const updateLinePrice = (line) => {
  if (line.quantity > 0) {
    line.price = parseFloat((line.total / line.quantity).toFixed(2))
  }
}

const handleProductChange = async (productId, line) => {
  const product = products.value.find(p => p.id === productId)
  if (product) {
    line.variant_id = null
    const primaryVar = product.variants?.find(v => v.is_primary) || product.variants?.[0]
    if (primaryVar && primaryVar.values?.length > 0) {
      line.variant_id = primaryVar.id
      line.price = primaryVar.price_override || product.price
    } else {
      line.price = product.price
    }
    updateLineTotal(line)
    
    // Fetch specification for BOM calculation if not cached
    if (productId && !specsCache.value[productId]) {
      try {
        const specs = await getProductSpecifications(productId)
        specsCache.value[productId] = specs
      } catch (e) {
        console.error('Failed to load spec for', productId)
      }
    }
    
    // Auto-select default specification ID
    const cachedSpecs = specsCache.value[productId]
    if (cachedSpecs && cachedSpecs.length) {
      const defaultSpec = cachedSpecs.find(s => s.is_default) || cachedSpecs[0]
      line.specification_id = defaultSpec.id
    }
  }
}

// Nomenclature Dialog Methods
const openNomenclatureDialog = (index) => {
  activeLineIndex.value = index
  nomenclatureSearch.value = ''
  selectedDialogProduct.value = null
  nomenclatureDialogVisible.value = true
}

const onDialogProductSelect = (val) => {
  selectedDialogProduct.value = val
}

const confirmDialogSelection = () => {
  if (selectedDialogProduct.value && activeLineIndex.value > -1) {
    const line = form.lines[activeLineIndex.value]
    line.product_id = selectedDialogProduct.value.id
    handleProductChange(line.product_id, line)
    nomenclatureDialogVisible.value = false
  }
}

// Variant Selector Methods
const openVariantSelector = (line) => {
  const product = products.value.find(p => p.id === line.product_id)
  if (!product) return
  activeLineForSelector.value = line
  selectedProductForSelector.value = product
  variantSelectorVisible.value = true
}

const onVariantSelected = (variant) => {
  if (activeLineForSelector.value) {
    activeLineForSelector.value.variant_id = variant.id || null
    activeLineForSelector.value._virtual_label = getVariantLabel(variant)
    activeLineForSelector.value._virtual_values = variant.values
    
    if (variant.id) {
      handleVariantChange(variant.id, activeLineForSelector.value)
    } else {
      const prod = products.value.find(p => p.id === activeLineForSelector.value.product_id)
      activeLineForSelector.value.price = calculatePriceWithRule(prod, variant.values)
      updateLineTotal(activeLineForSelector.value)
    }
  }
}

const clearVirtualVariant = (line) => {
  line._virtual_label = null
  line._virtual_values = null
}

const handleVariantChange = (variantId, line) => {
  const product = products.value.find(p => p.id === line.product_id)
  if (!product) return
  
  if (variantId) {
    const variant = product.variants?.find(v => v.id === variantId)
    if (variant) {
      if (product.price_rule?.pricing_mode === 'base_plus_markup') {
        line.price = calculatePriceWithRule(product, variant.values)
      } else {
        line.price = variant.price_override || product.price
      }
    }
  } else {
    line.price = product.price
  }
  updateLineTotal(line)
}

const calculatePriceWithRule = (product, values) => {
    if (!product) return 0
    if (!product.price_rule || product.price_rule.pricing_mode === 'manual') {
        // If specific variant has price_override, we might need it, but this helper is for rules.
        // For manual, we usually use variant.price_override directly in handleVariantChange.
        return product.price
    }
    
    let total = parseFloat(product.price_rule.base_price || 0)
    if (values && product.price_rule.markups) {
        values.forEach(v => {
            const markup = product.price_rule.markups.find(m => m.attribute_id === v.attribute_id && m.option_id === v.option_id)
            if (markup) total += parseFloat(markup.markup)
        })
    }
    return total
}

const getProductVariants = (productId) => {
  const product = products.value.find(p => p.id === productId)
  return product?.variants || []
}

const getVariantLabel = (variant) => {
  if (!variant) return ''
  if (!variant.values || variant.values.length === 0) return variant.sku || ''
  return variant.values.map(v => {
    const attrName = v.attribute?.name || ''
    const valText = v.option?.value || v.text_value || ''
    return attrName ? `${attrName}: ${valText}` : valText
  }).filter(Boolean).join(', ')
}

const getVariantLabelByLine = (line) => {
  if (!line.variant_id) return ''
  const variants = getProductVariants(line.product_id)
  const variant = variants.find(v => v.id === line.variant_id)
  return getVariantLabel(variant)
}

const fetchData = async () => {
  loading.value = true
  try {
    const [custRes, whRes, prodRes, statusRes, leadRes] = await Promise.all([
      api.get('/api/v1/counterparties', { params: { is_customer: true } }),
      api.get('/api/v1/warehouses'),
      api.get('/api/v1/products'),
      api.get('/api/v1/dictionaries/ORDER_STATUS'),
      api.get('/api/v1/dictionaries/LEAD_SOURCE').catch(() => ({ data: [] }))
    ])
    customers.value = custRes.data
    warehouses.value = whRes.data
    products.value = prodRes.data
    orderStatuses.value = statusRes.data
    leadSources.value = leadRes.data

    if (isEditMode.value) {
      const orderRes = await api.get(`/api/v1/orders/${route.params.id}`)
      const data = orderRes.data
      data.discount_percent = Number(data.discount_percent || 0)
      if (data.lines) {
        data.lines.forEach(line => {
          line.quantity = Number(line.quantity || 0)
          line.price = Number(line.price || 0)
          line.total = Number(line.total || 0)
        })
        // Fetch specs for existing lines and map null specification_id to default
        const uniqueProductIds = [...new Set(data.lines.map(l => l.product_id).filter(Boolean))]
        await Promise.all(uniqueProductIds.map(async pid => {
          if (!specsCache.value[pid]) {
            try {
              const specs = await getProductSpecifications(pid)
              specsCache.value[pid] = specs
            } catch (e) { console.error(e) }
          }
        }))
        
        data.lines.forEach(line => {
          if (!line.specification_id && specsCache.value[line.product_id]) {
            const cachedSpecs = specsCache.value[line.product_id]
            const defaultSpec = cachedSpecs.find(s => s.is_default) || cachedSpecs[0]
            if (defaultSpec) line.specification_id = defaultSpec.id
          }
        })
      }
      Object.assign(form, data)
    } else {
      const defaultWH = warehouses.value.find(w => w.is_default)
      if (defaultWH) {
        form.warehouse_id = defaultWH.id
      }
      addLine()
    }
  } catch (e) {
    console.error('Data loading error:', e)
    ElMessage.error('Помилка завантаження даних')
  } finally {
    loading.value = false
  }
}

const getStatusLabel = (code) => {
  const s = orderStatuses.value.find(i => i.code === code)
  return s?.name || code || '—'
}

const handleStatusChange = async (newStatus) => {
  if (form.status === newStatus) return
  const oldStatus = form.status
  form.status = newStatus
  try {
    const res = await api.put(`/api/v1/orders/${route.params.id}`, form)
    ElMessage.success('Статус оновлено')
  } catch (err) {
    form.status = oldStatus // Revert on failure
    console.error('Failed to change status:', err)
    ElMessage.error(err.response?.data?.detail || 'Помилка при зміні статусу')
  }
}

const saveOrder = async (action = 'save') => {
  if (!form.counterparty_id || !form.warehouse_id || form.lines.length === 0) {
    ElMessage.warning("Заповніть обов'язкові поля та додайте товари (мінімум 1 рядок)")
    return
  }
  
  // Logic for buttons
  // - "save" (Записати): always saves. If new, stays draft. 
  // - "post" (Провести): changes status to 'processing' if it is 'draft', saves.
  // - "post_close" (Провести та закрити): same as 'post', but goes back to list.
  
  if (action === 'post' || action === 'post_close') {
      if (form.status === 'draft') {
          const firstActive = orderStatuses.value.find(s => s.code !== 'draft')
          form.status = firstActive ? firstActive.code : 'processing' // Safe fallback
      }
  }

  const payload = {
    ...form,
    lines: form.lines.map(l => ({
        product_id: l.product_id,
        variant_id: l.variant_id,
        specification_id: l.specification_id || null,
        quantity: l.quantity,
        price: l.price,
        total: l.total,
        variant_values: l._virtual_values || undefined
    })),
    total_amount: totalAmount.value,
    shipping_date: form.shipping_date || null,
    contract: form.contract || null,
    comment: form.comment || null,
    discount_percent: form.discount_percent || 0
  }

  submitting.value = true
  try {
    if (isEditMode.value) {
      await api.put(`/api/v1/orders/${route.params.id}`, payload)
      ElMessage.success('Замовлення оновлено')
      if (action === 'post_close') {
          router.push('/sales/orders')
      } else {
          await fetchData()
      }
    } else {
      const res = await api.post('/api/v1/orders', payload)
      ElMessage.success('Замовлення створено')
      if (action === 'post_close') {
          router.push('/sales/orders')
      } else {
          router.push(`/sales/orders/${res.data.id}`)
      }
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка збереження')
  } finally {
    submitting.value = false
  }
}

const formatCurrency = (val) => new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(val || 0)
const formatShort = (val) => new Intl.NumberFormat('uk-UA').format(val) + ' грн'

onMounted(fetchData)

watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId && ['sales-order-edit', 'sales-order-new'].includes(route.name)) {
    if (!newId) {
      // Reset form to defaults when creating new
      Object.assign(form, {
        order_number: 'Авто',
        order_date: new Date().toISOString().split('T')[0],
        shipping_date: null,
        counterparty_id: '',
        warehouse_id: '',
        contract: '',
        comment: '',
        status: 'draft',
        discount_percent: 0,
        lines: []
      })
    }
    fetchData()
  }
})
</script>

<style scoped>
.erp-page-container {
  display: flex; flex-direction: column; height: 100%; overflow: hidden;
  background-color: #f6f7f9; font-family: 'Segoe UI', Arial, sans-serif;
}
.erp-toolbar {
  display: flex; align-items: center; justify-content: space-between; padding: 6px 12px;
  background-color: #fcfcfc; border-bottom: 1px solid #dcdfe6; flex-shrink: 0;
}
.erp-toolbar-left { display: flex; align-items: center; gap: 8px; }
.erp-toolbar-right { display: flex; align-items: center; gap: 6px; }
.erp-btn, .erp-btn-icon, .erp-btn-primary {
  border-radius: 2px !important; font-size: 13px !important; height: 28px !important;
  padding: 0 12px !important; border: 1px solid #dcdfe6 !important;
  background-color: #fff !important; color: #303133 !important;
}
.erp-btn:hover, .erp-btn-icon:hover { background-color: #f5f7fa !important; border-color: #c0c4cc !important; }
.erp-btn-primary {
  background-color: #eef2ff !important; border-color: #6366f1 !important;
  color: #4338ca !important; font-weight: 600 !important;
}
.erp-btn-primary:hover { background-color: #e0e7ff !important; }
.erp-btn-icon { padding: 0 8px !important; }
.erp-doc-info { margin-left: 16px; display: flex; align-items: center; }
.erp-doc-title { font-size: 14px; font-weight: 600; color: #303133; }

/* Header fields area */
.erp-header-fields {
  background-color: #f6f7f9; padding: 10px 16px 8px 16px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 6px; border-bottom: 1px solid #e4e7ed;
}
.erp-field-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.erp-field { display: flex; align-items: center; }
.erp-label { font-size: 15px; color: #374151; padding-right: 8px; white-space: nowrap; font-weight: 500; }
.erp-label.req { color: #f56c6c; }
.erp-input-wrapper { width: 160px; }
.client-select { width: 320px; }
.erp-header-fields :deep(.el-input__wrapper), .erp-header-fields :deep(.el-select__wrapper) {
  border-radius: 4px !important; box-shadow: none !important; border: 1px solid #d1d5db !important;
  background-color: #fff !important; min-height: 30px !important; height: 30px !important; padding: 0 10px !important;
}
.erp-header-fields :deep(.el-input__inner) {
  height: 28px !important; line-height: 28px !important; font-size: 15px !important; color: #111827 !important;
}
.erp-header-fields :deep(.el-select__wrapper) { min-height: 30px !important; }
.erp-link { font-size: 15px; color: #409eff; text-decoration: none; }
.erp-link:hover { text-decoration: underline; }

.erp-badges-group { display: flex; align-items: center; gap: 8px; }

/* Status Select Badge Styling */
.erp-status-select.success :deep(.el-select__wrapper) { background-color: #d1fae5 !important; border-color: #10b981 !important; color: #065f46 !important; font-weight: 600; }
.erp-status-select.success :deep(.el-select__placeholder) { color: #065f46 !important; }

.erp-status-select.primary :deep(.el-select__wrapper) { background-color: #dbeafe !important; border-color: #3b82f6 !important; color: #1e40af !important; font-weight: 600; }
.erp-status-select.primary :deep(.el-select__placeholder) { color: #1e40af !important; }

.erp-status-select.warning :deep(.el-select__wrapper) { background-color: #fef3c7 !important; border-color: #f59e0b !important; color: #92400e !important; font-weight: 600; }
.erp-status-select.warning :deep(.el-select__placeholder) { color: #92400e !important; }

.erp-status-select.danger :deep(.el-select__wrapper) { background-color: #fee2e2 !important; border-color: #ef4444 !important; color: #991b1b !important; font-weight: 600; }
.erp-status-select.danger :deep(.el-select__placeholder) { color: #991b1b !important; }

.erp-status-select.info :deep(.el-select__wrapper) { background-color: #f1f5f9 !important; border-color: #94a3b8 !important; color: #475569 !important; font-weight: 600; }
.erp-status-select.info :deep(.el-select__placeholder) { color: #475569 !important; }


/* Client info banner */
.client-info-banner {
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
  background-color: #f0f4ff; border: 1px solid #c7d2fe; border-radius: 6px;
  padding: 6px 12px; font-size: 12px; color: #4338ca; margin-top: 4px;
}
.client-info-item { display: flex; align-items: center; gap: 4px; }
.client-info-badge {
  margin-left: auto; background: #6366f1; color: #fff;
  border-radius: 10px; padding: 2px 10px; font-size: 11px;
}

/* Main body: flex row */
.order-body {
  flex: 1; display: flex; overflow: hidden; gap: 0;
}
.order-main {
  flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0;
}

/* Tabs */
.order-tabs { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.order-tabs :deep(.el-tabs__header) {
  margin: 0; background: #fff; padding: 0 12px;
  border-bottom: 1px solid #e4e7ed; flex-shrink: 0;
}
.order-tabs :deep(.el-tabs__item) { font-size: 13px; height: 38px; }
.order-tabs :deep(.el-tabs__item.is-active) { color: #6366f1; font-weight: 600; }
.order-tabs :deep(.el-tabs__active-bar) { background-color: #6366f1; }
.order-tabs :deep(.el-tabs__content) { flex: 1; overflow: auto; padding: 0; }
.order-tabs :deep(.el-tab-pane) { display: flex; flex-direction: column; height: 100%; }
.tab-badge { margin-left: 4px; }

/* Tab toolbar for items */
.tab-toolbar {
  display: flex; align-items: center; gap: 6px; padding: 8px 12px;
  background: #f6f7f9; border-bottom: 1px solid #e4e7ed; flex-shrink: 0;
}
.tab-toolbar-right { margin-left: auto; display: flex; align-items: center; gap: 6px; }

/* Table */
.erp-table-wrapper { flex: 1; padding: 0; overflow: hidden; }
.warehouse-select { width: 200px; }
.erp-dense-table { width: 100%; border: 1px solid #dcdfe6 !important; }
.erp-dense-table :deep(th.el-table__cell) {
  background-color: #f5f7fa !important; color: #606266; font-size: 12px;
  font-weight: 600; padding: 4px 0 !important; border-bottom: 1px solid #dcdfe6 !important; border-right: 1px solid #dcdfe6 !important;
}
.erp-dense-table :deep(td.el-table__cell) {
  padding: 0 !important; border-bottom: 1px solid #ebeef5 !important; border-right: 1px solid #ebeef5 !important;
}
.erp-dense-table :deep(.cell) { padding: 0 6px !important; line-height: 24px !important; }
.erp-cell-input { width: 100%; }
.erp-cell-input :deep(.el-input__wrapper), .erp-cell-input :deep(.el-select__wrapper) {
  box-shadow: none !important; border: 1px solid transparent !important; background-color: transparent !important;
  padding: 0 4px !important; border-radius: 2px !important; min-height: 24px !important; height: 24px !important;
}
.erp-cell-input :deep(.el-input__wrapper:focus-within), .erp-cell-input :deep(.el-input__wrapper:hover) {
  border-color: #dcdfe6 !important; background-color: #fff !important;
}
.erp-cell-input :deep(.el-input__inner) { font-size: 13px !important; height: 22px !important; line-height: 22px !important; }
.erp-cell-input.num :deep(.el-input__inner) { text-align: right !important; }
.erp-cell-trigger { width: 100%; height: 24px; display: flex; align-items: center; font-size: 13px; cursor: pointer; }
.virtual { color: #67c23a; }
.placeholder { color: #c0c4cc; }
.items-comment { padding: 8px 12px; background: #f6f7f9; border-top: 1px solid #e4e7ed; flex-shrink: 0; }
.erp-comment-input :deep(.el-textarea__inner) {
  border-radius: 2px; border: 1px solid #dcdfe6; font-size: 13px; padding: 6px;
}

/* Tab content card */
.tab-content-card {
  padding: 16px; display: flex; flex-direction: column; gap: 14px;
  max-width: 900px;
}

/* Fields grid */
.fields-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.fields-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.field-block { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 12px; color: #606266; font-weight: 500; }

/* Payment */
.payment-status-badge {
  display: inline-flex; align-items: center; padding: 4px 12px;
  border-radius: 20px; font-size: 12px; font-weight: 500; margin-top: 4px;
}
.ps-badge--green { background: #d1fae5; color: #065f46; }
.ps-badge--amber { background: #fef3c7; color: #92400e; }
.ps-badge--red { background: #fee2e2; color: #991b1b; }
.payment-summary-box {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
  padding: 12px 16px; display: flex; flex-direction: column; gap: 6px; max-width: 400px;
}
.ps-row { display: flex; justify-content: space-between; font-size: 13px; }
.ps-row--bold { font-weight: 600; }
.ps-divider { height: 1px; background: #e2e8f0; margin: 2px 0; }
.text-green { color: #059669; }
.text-red { color: #dc2626; }
.payments-list-title { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px; }

/* Documents */
.docs-actions { display: flex; gap: 8px; }
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; padding: 40px; color: #94a3b8; font-size: 13px;
}
.docs-list { display: flex; flex-direction: column; gap: 8px; }
.doc-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  border: 1px solid #e2e8f0; border-radius: 8px; background: #fff;
}
.doc-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.doc-name { font-size: 13px; font-weight: 500; color: #1e293b; }
.doc-meta { font-size: 11px; color: #94a3b8; }

/* Sidebar */
.order-sidebar {
  width: 280px; flex-shrink: 0; background: #fff; border-left: 1px solid #e4e7ed;
  overflow-y: auto; display: flex; flex-direction: column; gap: 0;
}
.sidebar-card {
  padding: 14px 16px; border-bottom: 1px solid #f0f2f5;
}
.sidebar-card-title {
  font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 1px solid #e4e7ed;
}
.summary-rows { display: flex; flex-direction: column; gap: 5px; margin-bottom: 10px; }
.sum-row { display: flex; justify-content: space-between; font-size: 12px; color: #606266; }
.sum-row--total { font-size: 14px; font-weight: 700; color: #1e293b; margin-top: 2px; }
.total-value { color: #6366f1; }
.sum-divider { height: 1px; background: #e4e7ed; margin: 3px 0; }
.discount-field {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12px; color: #606266; margin-top: 6px;
  padding-top: 6px; border-top: 1px solid #e4e7ed;
}

/* Quick actions */
.quick-actions { display: flex; flex-direction: column; gap: 6px; }
.qa-btn {
  width: 100%; justify-content: flex-start !important; text-align: left;
  height: 30px !important; font-size: 12px !important; margin-left: 0 !important;
  background: #f8fafc !important; border-color: #e2e8f0 !important; color: #374151 !important;
}
.qa-btn:hover { background: #eef2ff !important; border-color: #c7d2fe !important; color: #4338ca !important; }
.req { color: #f56c6c; }

/* Document Printing and Styling for BOM */
.bom-document {
  background: white;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1e293b;
  position: relative;
}

.bom-doc-actions {
  position: absolute;
  top: 15px;
  right: 15px;
}

.bom-doc-header {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e2e8f0;
}

.bom-doc-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #0f172a;
}

.bom-doc-meta {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #475569;
}

.bom-print-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.bom-print-table th, .bom-print-table td {
  border: 1px solid #cbd5e1;
  padding: 10px 12px;
  text-align: left;
}

.bom-print-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #334155;
}

@media print {
  body * {
    visibility: hidden;
  }
  .bom-document, .bom-document * {
    visibility: visible;
  }
  .bom-document {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    margin: 0;
    padding: 0;
    box-shadow: none;
    min-height: auto;
  }
  .no-print {
    display: none !important;
  }
  .bom-print-table th {
    background-color: #e2e8f0 !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>

