<template>
  <div class="crm-editor-page">

    <!-- ===== TOP BAR ===== -->
    <div class="crm-top-bar">
      <button class="crm-back-btn" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div class="crm-top-stages">
        <button
          v-for="(stage, idx) in stages"
          :key="stage.key"
          class="stage-pill"
          :class="{ active: form.crm_stage === stage.key, past: isPassedStage(idx) }"
          @click="setStage(stage.key)"
        >
          <span class="stage-pill-num">{{ idx + 1 }}</span>
          {{ stage.label }}
        </button>
      </div>
      <div class="crm-top-actions">
        <button class="crm-draft-btn" @click="save('draft')" :disabled="saving">
          Записати чернетку
        </button>
        <button class="crm-save-btn" @click="save('production')" :disabled="saving">
          <el-icon><Promotion /></el-icon>
          Зберегти та передати у виробництво
        </button>
      </div>
    </div>

    <!-- ===== BODY ===== -->
    <div class="crm-body" v-loading="loading">
      <div class="crm-left-col">

        <!-- ══ CLIENT BLOCK ══ -->
        <div class="crm-section">
          <div class="crm-section-head">
            <span class="crm-section-title">Клієнт</span>
              <el-select
                v-model="form.counterparty_id"
                filterable
                clearable
                placeholder="Оберіть або введіть клієнта"
                class="cp-select"
                :class="{ 'field-error': vErrors.client }"
                @change="onCounterpartyChange"
              >
              <el-option
                v-for="cp in counterparties"
                :key="cp.id"
                :label="cp.name"
                :value="cp.id"
              />
            </el-select>
            <button class="crm-link-btn" @click="showNewClientDialog = true">
              <el-icon><Plus /></el-icon> Новий клієнт
            </button>
          </div>

          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Ім'я та прізвище</label>
              <el-input v-model="clientName" placeholder="Олена Ковальчук" :class="{ 'field-error': vErrors.client }" />
            </div>
            <div class="crm-field">
              <label class="crm-label">Телефон</label>
              <el-input v-model="clientPhone" placeholder="+380 96 123 45 67" />
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Канал звернення</label>
            <div class="channel-pills">
              <button
                v-for="ch in leadSources"
                :key="ch.id"
                class="channel-pill"
                :class="{ active: form.lead_source_id === ch.id }"
                :style="{ 
                  '--pill-color': ch.color || '#94a3b8',
                  borderColor: form.lead_source_id === ch.id ? (ch.color || '#6366f1') : '#e2e8f0',
                  background: form.lead_source_id === ch.id ? (ch.color || '#6366f1') : 'transparent',
                  color: form.lead_source_id === ch.id ? '#fff' : '#475569'
                }"
                @click="form.lead_source_id = form.lead_source_id === ch.id ? null : ch.id"
              >{{ ch.name }}</button>
            </div>
          </div>


          <div class="crm-grid-2">
            <div class="crm-field">
              <label class="crm-label">Місто</label>
              <el-input v-model="form.city" placeholder="Київ" />
            </div>
            <div class="crm-field">
              <label class="crm-label">Доставка</label>
              <el-select v-model="form.delivery_method_id" placeholder="Оберіть" clearable style="width:100%">
                <el-option 
                  v-for="dm in deliveryMethods" 
                  :key="dm.id" 
                  :label="dm.name" 
                  :value="dm.id" 
                />
              </el-select>
            </div>

          </div>

          <!-- Nova Poshta branch — shown only when NP selected -->
          <div v-if="form.delivery_type === 'nova_poshta'" class="crm-field">
            <label class="crm-label">Відділення Нової Пошти</label>
            <el-input v-model="form.np_branch" placeholder="Наприклад: відділення №12" />
          </div>
        </div>

        <!-- ══ PRODUCT BLOCK ══ -->
        <div class="crm-section">
          <div class="crm-section-head">
            <span class="crm-section-title">Виріб</span>
            <span class="crm-attr-hint" v-if="productAttributes.length">
              <el-icon><Check /></el-icon>
              характеристики підтягнуто ({{ productAttributes.length }})
            </span>
          </div>

          <div class="crm-field">
            <label class="crm-label">Оберіть виріб з номенклатури</label>
            <el-select
              v-model="form.product_id"
              filterable
              placeholder="Почніть вводити назву..."
              style="width:100%"
              @change="onProductChange"
            >
              <el-option
                v-for="p in products"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              />
            </el-select>
            <p class="product-hint" v-if="selectedProduct">
              {{ selectedProduct.name }}
              <span v-if="productAttributes.length"> — підтягнуто {{ productAttributes.length }} характеристики</span>
            </p>
          </div>

          <!-- Dynamic attribute pills -->
          <div v-if="productAttributes.length" class="attributes-block">
            <div
              v-for="attr in productAttributes"
              :key="attr.id"
              class="attr-group"
            >
              <label class="crm-label">{{ attr.name }}</label>

              <!-- SELECT / COLOR — pill chooser -->
              <div v-if="['SELECT', 'COLOR'].includes(attr.type)" class="attr-pills">
                <button
                  v-for="opt in attr.options"
                  :key="opt.id"
                  class="attr-pill"
                  :class="{ active: form.attributes_values?.[attr.id] === opt.value }"
                  :style="attr.type === 'COLOR' && opt.color_code
                    ? { '--dot-color': opt.color_code }
                    : {}"
                  @click="setAttrValue(attr.id, opt.value)"
                >
                  <span v-if="attr.type === 'COLOR' && opt.color_code" class="attr-color-dot" :style="{ background: opt.color_code }" />
                  {{ opt.value }}
                </button>
              </div>

              <!-- DIMENSIONS — two inputs W × H -->
              <div v-else-if="attr.type === 'DIMENSIONS'" class="attr-dims">
                <el-input-number
                  :model-value="form.attributes_values?.[attr.id]?.w"
                  @update:model-value="v => setAttrDim(attr.id, 'w', v)"
                  :min="1" placeholder="Ш" size="small" style="width:90px"
                />
                <span class="dims-sep">×</span>
                <el-input-number
                  :model-value="form.attributes_values?.[attr.id]?.h"
                  @update:model-value="v => setAttrDim(attr.id, 'h', v)"
                  :min="1" placeholder="В" size="small" style="width:90px"
                />
                <span class="dims-unit">см</span>
              </div>

              <!-- TEXT / NUMBER — plain input -->
              <div v-else>
                <el-input
                  :model-value="form.attributes_values?.[attr.id]"
                  @update:model-value="v => setAttrValue(attr.id, v)"
                  size="small"
                  :placeholder="attr.name"
                  style="width:100%"
                />
              </div>
            </div>
          </div>

          <div class="crm-field">
            <label class="crm-label">Коментар до виробу</label>
            <el-input
              v-model="form.comment"
              type="textarea"
              :rows="3"
              placeholder="Індивідуальні побажання клієнта..."
            />
          </div>

          <!-- Reference photo -->
          <div class="crm-field">
            <label class="crm-label">Фото референс від клієнта</label>
            <div class="photo-upload-zone" @click="triggerPhotoUpload">
              <img v-if="form.reference_photo" :src="form.reference_photo" class="photo-preview" />
              <div v-else class="photo-placeholder">
                <el-icon><Picture /></el-icon>
                <span>+ Завантажити фото</span>
              </div>
            </div>
            <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="uploadPhoto" />
          </div>
        </div>

        <!-- ══ MATERIALS CHECK ══ -->
        <div class="crm-section" v-if="form.product_id">
          <div class="crm-section-head">
            <span class="crm-section-title">Матеріали на складі</span>
            <span class="mat-status-badge" :class="materialCheck.has_issues ? 'mat-warn' : 'mat-ok'">
              {{ materialCheck.has_issues ? 'є проблеми' : 'все є' }}
            </span>
          </div>

          <div v-if="materialsLoading" class="mat-loading">
            <el-icon class="is-loading"><Loading /></el-icon> Перевіряємо...
          </div>
          <div v-else-if="materialCheck.items.length" class="mat-list">
            <div
              v-for="item in materialCheck.items"
              :key="item.component_id"
              class="mat-row"
              :class="`mat-${item.status}`"
            >
              <span class="mat-name">{{ item.component_name }}</span>
              <span class="mat-req">потрібно: {{ formatQty(item.required_qty) }} {{ item.unit_of_measure }}</span>
              <span class="mat-stock-badge">
                <span class="mat-stock-icon">{{ item.status === 'ok' ? '[+]' : item.status === 'low' ? '[~]' : '[!]' }}</span>
                {{ formatQty(item.available_qty) }} {{ item.unit_of_measure }}
              </span>
            </div>
            <div v-if="materialCheck.has_issues" class="mat-order-row">
              <span>Не вистачає матеріалів — замовте до запуску</span>
              <button class="mat-order-btn" @click="goToPurchases">
                <el-icon><Promotion /></el-icon> Замовити
              </button>
            </div>
          </div>
          <div v-else class="mat-empty">Специфікація не знайдена для цього товару</div>
        </div>

      </div><!-- /left col -->

      <!-- ─── RIGHT SIDEBAR ─────────────────────────────────────── -->
      <div class="crm-right-col">

        <!-- ══ SUMMARY ══ -->
        <div class="crm-section crm-summary" style="background: #fff; border-radius: 12px; padding: 16px 18px; border: 1px solid #e2e8f0;">
          <div class="crm-section-title" style="margin-bottom:16px; font-size: 14px; font-weight: 700; color: #1e293b;">ПІДСУМОК ЗАМОВЛЕННЯ</div>

          <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
            <tr>
              <td style="width: 50%; padding-right: 8px; vertical-align: top;">
                <input
                  v-model.number="form.total_amount"
                  type="number"
                  style="font-size: 28px; font-weight: 700; color: #111827; border: none; border-bottom: 2px solid transparent; background: transparent; width: 100%; cursor: text; outline: none; padding-bottom: 4px; margin: 0;"
                  :class="{ 'field-error': vErrors.amount }"
                  placeholder="0"
                  @input="calcPrepayment"
                  @focus="$event.target.style.borderBottomColor = '#3D3AA8'"
                  @blur="$event.target.style.borderBottomColor = 'transparent'"
                /><br>
                <span style="font-size: 12px; color: #6B7280;">сума грн</span>
              </td>
              <td style="width: 50%; padding-left: 8px; vertical-align: top;">
                <input
                  v-model.number="form.prepayment_amount"
                  type="number"
                  style="font-size: 28px; font-weight: 700; color: #3D3AA8; border: none; border-bottom: 2px solid transparent; background: transparent; width: 100%; cursor: text; outline: none; padding-bottom: 4px; margin: 0;"
                  placeholder="0"
                  @input="onPrepaymentInput"
                  @focus="$event.target.style.borderBottomColor = '#3D3AA8'"
                  @blur="$event.target.style.borderBottomColor = 'transparent'"
                /><br>
                <span style="font-size: 12px; color: #6B7280;">
                  передоплата
                  <span v-if="form.total_amount > 0" style="color: #3D3AA8; font-weight: 600;">
                    ({{ Math.round((form.prepayment_amount || 0) / form.total_amount * 100) }}%)
                  </span>
                </span>
              </td>
            </tr>
          </table>

          <div style="margin-bottom: 20px;">
            <button
              v-for="pct in [20, 30, 50, 100]"
              :key="pct"
              :style="{
                borderRadius: '20px',
                padding: '5px 14px',
                border: '1.5px solid #E0E0FF',
                background: form.prepayment_percent === pct ? '#3D3AA8' : 'white',
                color: form.prepayment_percent === pct ? 'white' : '#3D3AA8',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                marginRight: '8px',
                marginBottom: '8px',
                display: 'inline-block',
                transition: 'all 0.2s'
              }"
              @click="setPrepayPct(pct)"
            >{{ pct }}%</button>
            <button
              :style="{
                borderRadius: '20px',
                padding: '5px 14px',
                border: '1.5px solid #E0E0FF',
                background: form.prepayment_percent === 0 ? '#3D3AA8' : 'white',
                color: form.prepayment_percent === 0 ? 'white' : '#3D3AA8',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'inline-block',
                transition: 'all 0.2s'
              }"
              @click="setPrepayPct(0)"
            >Без</button>
          </div>

          <div
            class="payment-badge-new"
            :style="{
              borderRadius: '8px',
              padding: '8px 14px',
              fontSize: '13px',
              fontWeight: '600',
              width: '100%',
              textAlign: 'center',
              display: 'flex',
              align-items: center,
              justify-content: center,
              gap: 8px,
              marginBottom: '20px',
              background: autoPaymentStatus.key === 'unpaid' ? '#F9FAFB' : autoPaymentStatus.key === 'partial' ? '#FFFBEB' : '#ECFDF5',
              color: autoPaymentStatus.key === 'unpaid' ? '#6B7280' : autoPaymentStatus.key === 'partial' ? '#92400E' : '#065F46'
            }"
          >
            <span
              class="status-dot-new"
              :style="{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: autoPaymentStatus.key === 'unpaid' ? '#9CA3AF' : autoPaymentStatus.key === 'partial' ? '#F59E0B' : '#10B981'
              }"
            />
            {{ autoPaymentStatus.label }}
          </div>

          <div class="crm-field" v-if="form.payment_status !== 'unpaid'" style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px;">
            <label class="crm-label" style="font-size: 12px; font-weight: 500; color: #64748b;">Рахунок для зарахування</label>
            <el-select v-model="form.bank_account_id" placeholder="Оберіть банк" style="width:100%">
              <el-option
                v-for="acc in bankAccounts"
                :key="acc.id"
                :label="`${acc.bank_name} (${acc.iban.slice(-4)})`"
                :value="acc.id"
              />
            </el-select>
          </div>

          <div class="crm-date-row" style="display: flex; justify-content: space-between; font-size: 12px; color: #475569; margin-top: 16px;">
            <div class="date-item">Дата: <span class="date-val" style="font-weight: 600; color: #1E293B;">{{ formatDate(form.order_date) }}</span></div>
            <div class="date-item">
              Дедлайн: 
              <span
                class="date-val"
                :style="{
                  fontWeight: 600,
                  color: form.deadline_date ? '#3D3AA8' : '#9CA3AF'
                }"
              >
                {{ form.deadline_date ? formatDate(form.deadline_date) : 'авто' }}
              </span>
            </div>
          </div>
        </div>

        <!-- ══ PRODUCTION ══ -->
        <div class="crm-section">
          <div class="crm-section-title" style="margin-bottom:10px">Виробництво</div>

          <div class="crm-field">
            <label class="crm-label">Пріоритет</label>
            <el-select v-model="form.priority" placeholder="Оберіть пріоритет" style="width:100%">
              <el-option
                v-for="p in priorities"
                :key="p.value"
                :label="p.label"
                :value="p.value"
              >
                <div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full" :style="{ background: p.color || '#94a3b8' }" />
                  {{ p.label }}
                </div>
              </el-option>
            </el-select>
          </div>


        </div>

        <!-- ══ КОМУНІКАЦІЯ ══ -->
        <div class="crm-section">
          <div class="comm-section-head">
            <span class="crm-section-title">Комунікація</span>
            <span class="attempts-badge" v-if="form.contact_attempts > 0">
              {{ form.contact_attempts }} {{ form.contact_attempts === 1 ? 'спроба' : 'спроби' }}
            </span>
          </div>

          <!-- New Compact Communication Block -->
          <div class="comm-compact-block">
            <div class="crm-field">
              <label class="crm-label">Канал зв'язку</label>
              <div class="comm-pills-row">
                <button
                  v-for="ct in communicationTypes"
                  :key="ct.code"
                  class="comm-pill"
                  :class="{ active: contactCommType === ct.code }"
                  @click="contactCommType = ct.code"
                  type="button"
                >
                  <span class="pill-icon">{{ ct.icon }}</span>
                  <span class="pill-name">{{ ct.name }}</span>
                </button>
              </div>
            </div>

            <div class="crm-field">
              <label class="crm-label">Результат контакту</label>
              <div class="results-grid-2x2">
                <button
                  v-for="cr in contactResults"
                  :key="cr.code"
                  class="result-tile"
                  :class="[cr.code.toLowerCase(), { active: contactResult === cr.code }]"
                  @click="contactResult = contactResult === cr.code ? null : cr.code"
                >
                  <span class="tile-icon">{{ cr.icon }}</span>
                  <span class="tile-label">{{ cr.name }}</span>
                </button>
              </div>
            </div>

            <!-- Compact Reminder Bar -->
            <Transition name="fade-slide">
              <div class="reminder-bar" v-if="['THINKING', 'NO_ANSWER'].includes(contactResult)">
                <div class="reminder-head">
                  <el-icon class="bell-icon"><Clock /></el-icon>
                  <span>Нагадати:</span>
                </div>
                <div class="reminder-pickers">
                  <el-date-picker
                    v-model="contactNextAt"
                    type="datetime"
                    size="small"
                    format="DD.MM HH:mm"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    placeholder="Дата та час"
                    class="compact-picker"
                  />
                </div>
              </div>
            </Transition>
          </div>

          <div class="crm-field">
            <label class="crm-label">Наступний контакт (план)</label>
            <el-date-picker
              v-model="form.next_contact_at"
              type="datetime"
              format="DD.MM.YYYY HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width:100%"
              placeholder="Вкажіть час наступного контакту"
            />
          </div>

          <div class="crm-field" v-if="contactResult === 'REFUSED'">
            <label class="crm-label">Причина відмови</label>
            <el-input v-model="contactNote" placeholder="Чому відмовився..." />
          </div>

          <button class="log-contact-btn" @click="logContact"
            :disabled="!contactResult || savingContact || !orderId">
            <el-icon v-if="savingContact" class="is-loading"><Loading /></el-icon>
            {{ orderId ? 'Записати результат' : 'Збережіть заявку, щоб записати контакт' }}
          </button>

          <div v-if="contacts.length" style="margin-top:20px">
            <div class="crm-section-title" style="margin-bottom:12px">Історія комунікацій</div>
            <div class="comm-timeline">
              <div
                v-for="c in contacts"
                :key="c.id"
                class="timeline-item"
              >
                <div class="timeline-dot" :style="{ background: getContactResultColor(c.result) }" />
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-channel">
                      {{ getCommIcon(c.communication_type) }} {{ getCommName(c.communication_type) }}
                    </span>
                    <span class="timeline-time">{{ formatDateTime(c.contacted_at) }}</span>
                  </div>
                  <div class="timeline-main">
                    <span class="timeline-res-badge" :style="{ background: getContactResultColor(c.result) + '15', color: getContactResultColor(c.result) }">
                      {{ contactResultLabel(c.result) }}
                    </span>
                    <span class="timeline-manager">
                      <el-icon><UserIcon /></el-icon> {{ c.manager?.name || 'Менеджер' }}
                    </span>
                  </div>
                  <div class="timeline-note" v-if="c.note">{{ c.note }}</div>
                  <div class="timeline-reminder" v-if="c.next_contact_at">
                    <el-icon><Clock /></el-icon> Нагадування: {{ formatDateTime(c.next_contact_at) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ══ HISTORY ══ -->
        <div class="crm-section">
          <div class="crm-section-title" style="margin-bottom:8px">Історія</div>
          <div class="history-list">
            <div class="history-item" v-for="(h, i) in history" :key="i">
              <span class="h-dot" />
              <div class="h-body">
                <span class="h-text">{{ h.text }}</span>
                <span class="h-time">{{ h.time }}</span>
              </div>
            </div>
          </div>

          <div class="crm-field" style="margin-top:10px">
            <label class="crm-label">Додати нотатку</label>
            <el-input
              v-model="form.internal_notes"
              type="textarea"
              :rows="3"
              placeholder="Запис менеджера..."
            />
          </div>
        </div>

      </div><!-- /right col -->
    </div><!-- /body -->

    <!-- ===== NEW CLIENT DIALOG ===== -->
    <el-dialog v-model="showNewClientDialog" title="Новий клієнт" width="460px">
      <div class="crm-grid-2">
        <div class="crm-field">
          <label class="crm-label">Ім'я та прізвище *</label>
          <el-input v-model="newClient.name" />
        </div>
        <div class="crm-field">
          <label class="crm-label">Телефон</label>
          <el-input v-model="newClient.phone" />
        </div>
      </div>
      <div class="crm-field">
        <label class="crm-label">Email</label>
        <el-input v-model="newClient.email" />
      </div>
      <template #footer>
        <el-button @click="showNewClientDialog = false">Скасувати</el-button>
        <el-button type="primary" @click="createNewClient" :loading="savingClient">Створити</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Plus, Check, Promotion, Picture, Loading, Clock, User as UserIcon
} from '@element-plus/icons-vue'
import api from '@/api'
import { useUserStore } from '@/stores/user'

const router    = useRouter()
const route     = useRoute()
const userStore = useUserStore()
const orderId   = computed(() => route.params.id !== 'new' ? route.params.id : null)

// ─── State ────────────────────────────────────────────────────────────────────
const loading        = ref(false)
const saving         = ref(false)
const savingClient   = ref(false)
const materialsLoading = ref(false)
const products       = ref([])
const counterparties = ref([])
const users          = ref([])
const productAttributes = ref([])
const showNewClientDialog = ref(false)
const photoInput     = ref(null)

const leadSources = ref([])
const paymentStatusesRes = ref([])
const prioritiesRes = ref([])
const bankAccounts = ref([])
const deliveryMethods = ref([])

const defaultCommTypes = [
  { code: 'CALL', name: 'Дзвінок', icon: '📞' },
  { code: 'VIBER', name: 'Viber', icon: '💬' },
  { code: 'TELEGRAM', name: 'Telegram', icon: '✈️' },
  { code: 'INSTAGRAM', name: 'Instagram', icon: '📸' },
  { code: 'EMAIL', name: 'Email', icon: '✉️' },
  { code: 'MEET', name: 'Зустріч', icon: '🤝' },
]
const communicationTypes = ref([...defaultCommTypes])

const defaultContactResults = [
  { code: 'NO_ANSWER', name: 'Не відповів', icon: '🔴' },
  { code: 'THINKING',  name: 'Думає',      icon: '🤔' },
  { code: 'REFUSED',   name: 'Відмовився',  icon: '✗' },
  { code: 'CONFIRMED', name: 'Підтвердив', icon: '✓' },
]
const contactResults = ref([...defaultContactResults])

const materialCheck = reactive({ has_issues: false, items: [] })

const newClient = reactive({ name: '', phone: '', email: '' })


// Communication
const contacts      = ref([])
const contactResult = ref(null)
const contactCommType = ref('CALL')
const contactNote   = ref('')
const contactNextAt = ref(null)
const savingContact = ref(false)

const vErrors = reactive({
  client: false,
  amount: false
})

// Watch contact result to auto-set reminder
watch(() => contactResult.value, (newVal) => {
  if (newVal === 'NO_ANSWER') {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    // Format to local ISO-like string YYYY-MM-DDTHH:mm:ss
    const pad = (n) => String(n).padStart(2, '0')
    const y = tomorrow.getFullYear()
    const m = pad(tomorrow.getMonth() + 1)
    const d = pad(tomorrow.getDate())
    const hh = pad(tomorrow.getHours())
    const mm = pad(tomorrow.getMinutes())
    const ss = pad(tomorrow.getSeconds())
    
    contactNextAt.value = `${y}-${m}-${d}T${hh}:${mm}:${ss}`
  }
})

// Sync comm type with lead source for new orders
watch(() => contactCommType.value, (newVal) => {
  if (!orderId.value && newVal) {
    // Try to find matching lead source by name or code
    const found = leadSources.value.find(ls => ls.id === newVal || ls.name === newVal)
    if (found) form.lead_source_id = found.id
  }
})

const form = reactive({
  order_number:   'Авто',
  order_date:     new Date().toISOString().slice(0, 10),
  counterparty_id: null,
  warehouse_id:   null,
  product_id:     null,
  crm_stage:      route.query.stage || 'new',
  lead_source_id: null,
  channel:        null,
  city:           null,
  delivery_type:  null,
  attributes_values: {},
  total_amount:   0,
  paid_amount:    0,
  payment_status: 'unpaid',
  prepayment_percent: null,
  prepayment_amount:  null,
  deadline_date:  null,
  next_contact_date: null,
  priority:       'normal',
  manager_id:     null,
  comment:          null,
  internal_notes:   null,
  reference_photo:  null,
  discount_percent: 0,
  np_branch:        null,
  next_contact_at:  null,
  contact_attempts: 0,
})

// Client quick-edit fields (synced to counterparty)
const clientName  = ref('')
const clientPhone = ref('')

// Config fetched during loadData
const stages = [
  { key: 'new',        label: 'Нова заявка' },
  { key: 'processing', label: 'В обробці' },
  { key: 'confirmed',  label: 'Підтверджено' },
  { key: 'payment',    label: 'Оплата' },
  { key: 'production', label: 'У виробництві' },
  { key: 'done',       label: 'Виконано' },
]
const stageIndex = computed(() => stages.findIndex(s => s.key === form.crm_stage))
const isPassedStage = (idx) => idx < stageIndex.value

// Dictionaries fetched in onMounted
const priorities = computed(() => prioritiesRes.value.map(i => ({ value: i.id, label: i.name, color: i.color })))
const paymentStatuses = computed(() => paymentStatusesRes.value.map(i => ({ value: i.id, label: i.name, color: i.color })))


// ─── Computed ─────────────────────────────────────────────────────────────────
const selectedProduct = computed(() => products.value.find(p => p.id === form.product_id) || null)

const history = computed(() => {
  const items = []
  if (orderId.value) {
    items.push({ text: 'Заявка створена', time: formatDate(form.order_date) })
    if (form.crm_stage !== 'new') {
      items.push({ text: `Переведено у «${stages.find(s => s.key === form.crm_stage)?.label}»`, time: 'раніше' })
    }
  } else {
    items.push({ text: 'Заявка створена', time: 'щойно' })
  }
  return items
})

const autoPaymentStatus = computed(() => {
  const total = Number(form.total_amount) || 0
  const paid = Number(form.prepayment_amount) || 0
  
  if (paid === 0) return { label: 'Не оплачено', color: '#94a3b8', key: 'unpaid' }
  if (paid >= total && total > 0) return { label: 'Оплачено повністю', color: '#22c55e', key: 'paid' }
  return { label: 'Часткова оплата', color: '#eab308', key: 'partial' }
})

watch(() => autoPaymentStatus.value, (newVal) => {
  form.payment_status = newVal.key
}, { immediate: true })

// ─── Helpers ──────────────────────────────────────────────────────────────────
const formatCurrency = (v) => Number(v || 0).toLocaleString('uk-UA', { minimumFractionDigits: 0 })
const formatQty = (v) => Number(v || 0).toLocaleString('uk-UA', { minimumFractionDigits: 0, maximumFractionDigits: 3 })
const formatDate = (d) => {
  if (!d) return ''
  const [y, m, day] = (d || '').split('-')
  return `${day}.${m}.${y}`
}

// ─── Attribute helpers ────────────────────────────────────────────────────────
const setAttrValue = (attrId, value) => {
  form.attributes_values = { ...form.attributes_values, [attrId]: value }
}
const setAttrDim = (attrId, axis, value) => {
  const cur = form.attributes_values?.[attrId] || {}
  form.attributes_values = { ...form.attributes_values, [attrId]: { ...cur, [axis]: value } }
}

// ─── Prepayment calc ──────────────────────────────────────────────────────────
const setPrepayPct = (pct) => {
  form.prepayment_percent = pct
  calcPrepayment()
}
const calcPrepayment = () => {
  if (form.prepayment_percent > 0) {
    form.prepayment_amount = Math.round(form.total_amount * form.prepayment_percent / 100)
  } else if (form.prepayment_percent === 0) {
    form.prepayment_amount = 0
  }
}
const onPrepaymentInput = () => {
  if (form.total_amount > 0) {
    form.prepayment_percent = Math.round((form.prepayment_amount || 0) / form.total_amount * 100)
  } else {
    form.prepayment_percent = 0
  }
}

// ─── Stage ────────────────────────────────────────────────────────────────────
const setStage = (key) => { form.crm_stage = key }

// ─── Counterparty change ──────────────────────────────────────────────────────
const onCounterpartyChange = (id) => {
  const cp = counterparties.value.find(c => c.id === id)
  if (cp) {
    clientName.value  = cp.name
    clientPhone.value = cp.phone || ''
  }
}

// ─── Product change ───────────────────────────────────────────────────────────
const onProductChange = async (productId) => {
  productAttributes.value = []
  form.attributes_values = {}
  materialCheck.items = []
  materialCheck.has_issues = false

  if (!productId) return

  try {
    // Fetch category attributes for this product
    const product = products.value.find(p => p.id === productId)
    if (product?.category) {
      const res = await api.get(`/api/v1/attributes/category/${product.category}`)
      productAttributes.value = res.data
        ?.map(ca => ca.attribute)
        .filter(a => a && !a.is_archived) || []
    }
    // Auto-fill total amount from product price if available and not already set
    if (product?.price && Number(product.price) > 0) {
      form.total_amount = Number(product.price)
      calcPrepayment()
    }
  } catch { /* no attributes */ }

  // Check materials if we already have an order ID
  await checkMaterials(productId)
}

const checkMaterials = async (productId) => {
  if (!productId) return
  materialsLoading.value = true
  try {
    const pid = orderId.value || 'new'
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}/material-check?product_id=${productId}`)
      Object.assign(materialCheck, res.data)
    } else {
      // For new orders, fetch spec directly
      const specRes = await api.get(`/api/v1/products/${productId}/specifications`)
      const specs = specRes.data || []
      const defaultSpec = specs.find(s => s.is_default && s.is_active) || specs[0]
      if (!defaultSpec?.items?.length) { materialsLoading.value = false; return }

      // Get stock for each component
      const items = []
      let hasIssues = false
      for (const item of defaultSpec.items) {
        const stockRes = await api.get(`/api/v1/products/${item.component_id}/stock`)
        const avail = stockRes.data?.total_quantity || 0
        const req = Number(item.quantity)
        const st = avail >= req ? 'ok' : avail > 0 ? 'low' : 'missing'
        if (st !== 'ok') hasIssues = true
        items.push({
          component_id: item.component_id,
          component_name: item.component?.name || item.component_id,
          component_sku: item.component?.sku || '',
          unit_of_measure: item.unit_of_measure || item.component?.unit_of_measure || 'шт',
          required_qty: req,
          available_qty: avail,
          status: st,
        })
      }
      materialCheck.items = items
      materialCheck.has_issues = hasIssues
    }
  } catch { /* silent */ } finally {
    materialsLoading.value = false
  }
}

// ─── Photo upload ─────────────────────────────────────────────────────────────
const triggerPhotoUpload = () => photoInput.value?.click()
const uploadPhoto = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await api.post('/api/v1/upload/image', fd)
    form.reference_photo = res.data.url
  } catch {
    ElMessage.error('Помилка завантаження фото')
  }
}

// ─── New client ───────────────────────────────────────────────────────────────
const createNewClient = async () => {
  if (!newClient.name) { ElMessage.warning('Вкажіть ім\'я'); return }
  savingClient.value = true
  try {
    const res = await api.post('/api/v1/counterparties', {
      name: newClient.name,
      phone: newClient.phone,
      email: newClient.email,
      is_customer: true,
      is_supplier: false,
    })
    counterparties.value.push(res.data)
    form.counterparty_id = res.data.id
    clientName.value  = res.data.name
    clientPhone.value = res.data.phone || ''
    showNewClientDialog.value = false
    Object.assign(newClient, { name: '', phone: '', email: '' })
    ElMessage.success('Клієнта створено')
  } catch {
    ElMessage.error('Помилка створення клієнта')
  } finally {
    savingClient.value = false
  }
}

// ─── Go to purchases ──────────────────────────────────────────────────────────
const goToPurchases = () => router.push('/purchases/orders/new')

// ─── Communication helpers ────────────────────────────────────────────────────
const formatDateTime = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleString('uk-UA', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const loadContacts = async () => {
  if (!orderId.value) return
  try {
    const res = await api.get(`/api/v1/crm/orders/${orderId.value}/contacts`)
    contacts.value = res.data
  } catch { /* silent */ }
}

const getCommName = (code) => {
  const ct = communicationTypes.value.find(i => i.code === code)
  return ct ? ct.name : 'Контакт'
}
const getCommIcon = (code) => {
  const ct = communicationTypes.value.find(i => i.code === code)
  return ct ? ct.icon : '📞'
}
const contactResultIcon = (code) => {
  const cr = contactResults.value.find(i => i.code === code)
  return cr ? cr.icon : '📞'
}
const contactResultLabel = (code) => {
  const cr = contactResults.value.find(i => i.code === code)
  return cr ? cr.name : code
}
const getContactResultColor = (code) => {
  const cr = contactResults.value.find(i => i.code === code)
  return cr ? cr.color : '#e2e8f0'
}

const logContact = async () => {
  if (!contactResult.value) return
  savingContact.value = true
  try {
    await api.post(`/api/v1/crm/orders/${orderId.value}/contacts`, {
      result: contactResult.value,
      communication_type: contactCommType.value,
      note: contactNote.value || null,
      next_contact_at: contactNextAt.value || null,
    })
    ElMessage.success('Контакт записано')
    contactResult.value = null
    contactNote.value = ''
    contactNextAt.value = null
    await loadData()  // reload to reflect updated stage / attempts / next_contact_at
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка запису контакту')
  } finally {
    savingContact.value = false
  }
}

// ─── Save ─────────────────────────────────────────────────────────────────────
const save = async (action) => {
  vErrors.client = !form.counterparty_id && !clientName.value
  vErrors.amount = !form.total_amount || form.total_amount <= 0

  if (vErrors.client || vErrors.amount) {
    ElMessage.warning('Заповніть обов\'язкові поля: Клієнт, Сума')
    return
  }

  // Auto-pick warehouse if not set
  if (!form.warehouse_id) {
    try {
      const wRes = await api.get('/api/v1/warehouses?limit=1')
      if (wRes.data?.[0]) form.warehouse_id = wRes.data[0].id
      else { ElMessage.warning('Не знайдено жодного складу'); return }
    } catch { ElMessage.warning('Не вдалося отримати склад'); return }
  }

  saving.value = true
  try {
    // Merge NP branch into attributes_values (JSONB)
    const mergedAttrs = { ...form.attributes_values }
    if (form.np_branch) mergedAttrs._np_branch = form.np_branch
    else                delete mergedAttrs._np_branch

    const payload = {
      order_number:       form.order_number,
      order_date:         form.order_date,
      counterparty_id:    form.counterparty_id,
      warehouse_id:       form.warehouse_id,
      total_amount:       form.total_amount,
      discount_percent:   form.discount_percent,
      crm_stage:          form.crm_stage,
      channel:            form.channel,
      lead_source_id:     form.lead_source_id,
      city:               form.city,
      delivery_type:      form.delivery_type,
      delivery_method_id: form.delivery_method_id,
      attributes_values:  mergedAttrs,
      paid_amount:        form.paid_amount,
      payment_status:     form.payment_status,
      payment_status_id:  form.payment_status_id,
      prepayment_percent: form.prepayment_percent,
      prepayment_amount:  form.prepayment_amount,
      deadline_date:      form.deadline_date,
      next_contact_at:    form.next_contact_at,
      priority:           form.priority,
      priority_id:        form.priority_id,
      manager_id:         form.manager_id,
      cancel_reason_id:   form.cancel_reason_id,
      client_type_id:     form.client_type_id,
      comment:            form.comment,
      internal_notes:     form.internal_notes,
      reference_photo:    form.reference_photo,

      lines: form.product_id ? [{
        product_id: form.product_id,
        quantity:   1,
        price:      form.total_amount,
        total:      form.total_amount,
      }] : [],
    }

    // 1. Save / update the order
    let savedOrder
    if (orderId.value) {
      const res = await api.put(`/api/v1/orders/${orderId.value}`, payload)
      savedOrder = res.data
    } else {
      const res = await api.post('/api/v1/orders', payload)
      savedOrder = res.data
    }

    // 2. If "send to production" — call dedicated endpoint that sets stage + creates ProductionOrder
    if (action === 'production') {
      try {
        const prodRes = await api.post(`/api/v1/orders/${savedOrder.id}/send-to-production`)
        ElMessage.success(`Передано у виробництво! Завдання ${prodRes.data.production_order_number} створено`)
        router.push(`/production/orders/${prodRes.data.production_order_id}`)
        return
      } catch (err) {
        ElMessage.error('Замовлення збережено, але помилка при створенні завдання: ' + (err.response?.data?.detail || ''))
        router.push(`/crm/orders/${savedOrder.id}`)
        return
      }
    }

    ElMessage.success('Збережено як чернетку')
    router.push(`/crm/orders/${savedOrder.id}`)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Помилка збереження')
  } finally {
    saving.value = false
  }
}

// ─── Load ─────────────────────────────────────────────────────────────────────
const loadData = async () => {
  loading.value = true
  try {
    const [pRes, cpRes, usersRes] = await Promise.allSettled([
      api.get('/api/v1/products?limit=500'),
      api.get('/api/v1/counterparties?limit=500&is_customer=true'),
      api.get('/users/colleagues'),
    ])
    products.value       = pRes.status       === 'fulfilled' ? pRes.value.data       : []
    counterparties.value = cpRes.status      === 'fulfilled' ? cpRes.value.data      : []
    users.value          = usersRes.status   === 'fulfilled' ? usersRes.value.data   : []

    // 1. Load Dictionaries (always needed, even for new orders)
    try {
      const [ls, ps, pr, dm, ct, cr, accs] = await Promise.all([
        api.get('/api/v1/dictionaries/LEAD_SOURCE'),
        api.get('/api/v1/dictionaries/PAYMENT_STATUS'),
        api.get('/api/v1/dictionaries/PRIORITY'),
        api.get('/api/v1/dictionaries/DELIVERY_METHOD'),
        api.get('/api/v1/dictionaries/COMMUNICATION_TYPE'),
        api.get('/api/v1/dictionaries/CONTACT_RESULT'),
        api.get('/api/v1/companies/default/accounts').catch(() => ({ data: [] }))
      ])
      leadSources.value = ls.data
      paymentStatusesRes.value = ps.data
      prioritiesRes.value = pr.data
      deliveryMethods.value = dm.data
      communicationTypes.value = ct.data
      contactResults.value = cr.data
      bankAccounts.value = accs.data
    } catch (e) {
      console.warn('Non-critical dictionaries failed to load', e)
    }

    // Ensure dictionaries have fallback data if API returns empty
    if (!communicationTypes.value || communicationTypes.value.length === 0) {
      communicationTypes.value = [...defaultCommTypes]
    }
    if (!contactResults.value || contactResults.value.length === 0) {
      contactResults.value = [...defaultContactResults]
    }
    if (!leadSources.value || leadSources.value.length === 0) {
      // Use comm types as fallback for lead sources if empty
      leadSources.value = communicationTypes.value.map(ct => ({ id: ct.code, name: ct.name, color: '#6366f1' }))
    }

    // 2. Load existing Order data
    if (orderId.value) {
      const res = await api.get(`/api/v1/orders/${orderId.value}`)
      const o = res.data
      Object.assign(form, o)
      // Map new fields
      form.lead_source_id = o.lead_source_id
      form.delivery_method_id = o.delivery_method_id
      form.payment_status_id = o.payment_status_id
      form.priority_id = o.priority_id
      form.cancel_reason_id = o.cancel_reason_id
      form.client_type_id = o.client_type_id
      Object.assign(form, {
        order_number:    o.order_number,
        order_date:      o.order_date,
        counterparty_id: o.counterparty_id,
        warehouse_id:    o.warehouse_id,
        product_id:      o.lines?.[0]?.product_id || null,
        crm_stage:       o.crm_stage || 'new',
        channel:         o.channel,
        city:            o.city,
        delivery_type:   o.delivery_type,
        attributes_values: (() => {
          const av = { ...(o.attributes_values || {}) }
          delete av._np_branch; delete av._client_status
          return av
        })(),
        np_branch:        o.attributes_values?._np_branch || null,
        next_contact_at:  o.next_contact_at || null,
        contact_attempts: o.contact_attempts || 0,
        total_amount:     Number(o.total_amount),
        paid_amount:     Number(o.paid_amount || 0),
        payment_status:  o.payment_status || 'unpaid',
        prepayment_percent: o.prepayment_percent ? Number(o.prepayment_percent) : null,
        prepayment_amount:  o.prepayment_amount ? Number(o.prepayment_amount) : null,
        deadline_date:   o.deadline_date,
        next_contact_date: o.next_contact_date,
        priority:        o.priority || 'normal',
        manager_id:      o.manager_id,
        comment:         o.comment,
        internal_notes:  o.internal_notes,
        reference_photo: o.reference_photo,
        discount_percent: Number(o.discount_percent || 0),
      })
      if (form.product_id) await onProductChange(form.product_id)

      const cp = counterparties.value.find(c => c.id === form.counterparty_id)
      if (cp) {
        clientName.value = cp.name
        clientPhone.value = cp.phone || ''
      }

      await loadContacts()
    }
  } catch (err) {
    ElMessage.error('Помилка завантаження: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
/* ─── Page ────────────────────────────────────────────────────────────────── */
.crm-editor-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #f1f5f9;
  font-family: 'Inter', sans-serif;
}

/* ─── Top Bar ─────────────────────────────────────────────────────────────── */
.crm-top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.crm-back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 8px;
  border: 1px solid #e2e8f0; background: transparent;
  color: #64748b; cursor: pointer;
}
.crm-back-btn:hover { background: #f8fafc; }

.crm-top-stages {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 0;
  overflow-x: auto;
}
.stage-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border-right: none;
  white-space: nowrap;
  transition: background 0.12s, color 0.12s;
}
.stage-pill:first-child { border-radius: 8px 0 0 8px; }
.stage-pill:last-child  { border-radius: 0 8px 8px 0; border-right: 1px solid #e2e8f0; }
.stage-pill.past   { background: #e0e7ff; color: #4338ca; border-color: #c7d2fe; }
.stage-pill.active { background: #6366f1; color: #fff; border-color: #6366f1; z-index: 1; }
.stage-pill-num {
  width: 18px; height: 18px; border-radius: 50%;
  background: rgba(255,255,255,.3);
  font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.stage-pill.active .stage-pill-num { background: rgba(255,255,255,.35); }

.crm-top-actions { display: flex; gap: 8px; align-items: center; }
.crm-draft-btn {
  padding: 7px 14px; border-radius: 8px;
  border: 1px solid #e2e8f0; background: #fff;
  font-size: 12px; font-weight: 500; color: #475569; cursor: pointer;
}
.crm-draft-btn:hover { background: #f8fafc; }
.crm-save-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: 8px; border: none;
  background: #6366f1; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer;
}
.crm-save-btn:hover { background: #4f46e5; }

/* ─── Body ────────────────────────────────────────────────────────────────── */
.crm-body {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}
.crm-left-col  { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 14px; }
.crm-right-col { width: 320px; flex-shrink: 0; display: flex; flex-direction: column; gap: 14px; }

/* ─── Section ─────────────────────────────────────────────────────────────── */
.crm-section {
  background: #fff;
  border-radius: 12px;
  padding: 16px 18px;
  border: 1px solid #e2e8f0;
}
.crm-section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.crm-section-title { font-size: 14px; font-weight: 700; color: #1e293b; }
.crm-attr-hint {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; color: #10b981; font-weight: 500;
}
.cp-select { flex: 1; min-width: 200px; }
.crm-link-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 6px;
  border: 1px dashed #c7d2fe; background: transparent;
  color: #6366f1; font-size: 12px; cursor: pointer;
}
.crm-link-btn:hover { background: #eef2ff; }

/* ─── Fields ──────────────────────────────────────────────────────────────── */
.crm-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.crm-field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }
.crm-label { font-size: 12px; font-weight: 500; color: #64748b; }

/* ─── Channel pills ───────────────────────────────────────────────────────── */
.channel-pills { display: flex; flex-wrap: wrap; gap: 6px; }
.channel-pill {
  padding: 4px 12px; border-radius: 99px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; color: #475569;
  cursor: pointer; transition: all 0.12s;
}
.channel-pill.active { border-color: currentColor; }
.ch-instagram.active { background: #fce7f3; color: #9d174d; border-color: #f9a8d4; }
.ch-website.active   { background: #dbeafe; color: #1e40af; border-color: #93c5fd; }
.ch-referral.active  { background: #d1fae5; color: #065f46; border-color: #6ee7b7; }
.ch-telegram.active  { background: #e0f2fe; color: #0369a1; border-color: #7dd3fc; }
.ch-olx.active       { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
.ch-phone.active     { background: #f3e8ff; color: #6b21a8; border-color: #d8b4fe; }

/* ─── Product hint ────────────────────────────────────────────────────────── */
.product-hint { font-size: 11px; color: #94a3b8; margin: 4px 0 0; }

/* ─── Attributes block ────────────────────────────────────────────────────── */
.attributes-block { display: flex; flex-direction: column; gap: 12px; margin-bottom: 12px; }
.attr-group { border-left: 3px solid #e0e7ff; padding-left: 10px; }
.attr-pills { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.attr-pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; color: #475569; cursor: pointer;
  transition: all 0.12s;
}
.attr-pill.active { background: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 600; }
.attr-color-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }

.attr-dims { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
.dims-sep  { font-size: 16px; color: #94a3b8; }
.dims-unit { font-size: 12px; color: #94a3b8; }

/* ─── Photo upload ────────────────────────────────────────────────────────── */
.photo-upload-zone {
  border: 2px dashed #e2e8f0; border-radius: 10px;
  min-height: 100px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; overflow: hidden; transition: border-color 0.15s;
}
.photo-upload-zone:hover { border-color: #6366f1; }
.photo-placeholder {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: #94a3b8; font-size: 13px;
}
.photo-placeholder .el-icon { font-size: 24px; }
.photo-preview { max-width: 100%; max-height: 200px; border-radius: 8px; }

/* ─── Material check ──────────────────────────────────────────────────────── */
.mat-status-badge {
  font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 99px;
}
.mat-ok   { background: #d1fae5; color: #065f46; }
.mat-warn { background: #fef3c7; color: #92400e; }
.mat-loading { color: #94a3b8; font-size: 13px; display: flex; align-items: center; gap: 6px; }

.mat-list { display: flex; flex-direction: column; gap: 4px; }
.mat-row {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 10px; border-radius: 8px; font-size: 12px;
}
.mat-ok      { background: #f0fdf4; }
.mat-low     { background: #fffbeb; }
.mat-missing { background: #fff1f2; }
.mat-name  { flex: 1; font-weight: 500; color: #1e293b; }
.mat-req   { color: #94a3b8; white-space: nowrap; }
.mat-stock-badge { font-weight: 700; white-space: nowrap; }
.mat-ok      .mat-stock-badge { color: #16a34a; }
.mat-low     .mat-stock-badge { color: #d97706; }
.mat-missing .mat-stock-badge { color: #dc2626; }

.mat-order-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 10px; background: #fff1f2; border-radius: 8px;
  font-size: 12px; color: #9f1239; font-weight: 500;
}
.mat-order-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 12px; border-radius: 7px; border: none;
  background: #ef4444; color: #fff; font-size: 12px; font-weight: 600; cursor: pointer;
}
.mat-empty { font-size: 12px; color: #94a3b8; text-align: center; padding: 10px; }

/* ─── Summary ─────────────────────────────────────────────────────────────── */
.summary-stats {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 8px; margin-bottom: 14px;
}
.sum-stat {
  background: #f8fafc; border-radius: 8px; padding: 10px 12px; text-align: center;
}
.sum-stat-val   { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 2px; }
.sum-stat-label { font-size: 11px; color: #94a3b8; margin: 0; }

.prepay-pills { display: flex; flex-wrap: wrap; gap: 6px; }
.prepay-pill {
  padding: 4px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; color: #475569; cursor: pointer;
}
.prepay-pill.active { background: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 700; }
.prepay-pill.pay-none.active { background: #f1f5f9; border-color: #94a3b8; color: #475569; }

.pay-status-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.pay-status-pill {
  padding: 5px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; cursor: pointer;
}
.psp-unpaid.active  { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }
.psp-partial.active { background: #fef3c7; border-color: #fcd34d; color: #92400e; }
.psp-paid.active    { background: #d1fae5; border-color: #6ee7b7; color: #065f46; }

.payment-status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.deadline-hint { font-size: 11px; color: #94a3b8; margin: 4px 0 0; }

/* ─── Priority pills ──────────────────────────────────────────────────────── */
.priority-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.priority-pill {
  padding: 5px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; cursor: pointer;
}
.pp-normal.active   { background: #eef2ff; border-color: #6366f1; color: #4338ca; }
.pp-urgent.active   { background: #fffbeb; border-color: #fcd34d; color: #92400e; }
.pp-critical.active { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }

/* ─── Communication section ──────────────────────────────────────────────── */
.comm-section-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.attempts-badge {
  font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 99px;
  background: #fee2e2; color: #991b1b;
}
.comm-type-list { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.comm-type-btn {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 4px; padding: 10px; min-width: 65px; border-radius: 12px;
  border: 1.5px solid #e2e8f0; background: #f8fafc; cursor: pointer;
  transition: all 0.15s;
}
.comm-type-btn:hover { background: #eef2ff; border-color: #c7d2fe; }
.comm-type-btn.active {
  background: #eef2ff; border-color: #6366f1; transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.1);
}
.ct-icon { font-size: 20px; }
.ct-name { font-size: 10px; font-weight: 600; color: #64748b; text-align: center; line-height: 1.1; }
.comm-type-btn.active .ct-name { color: #6366f1; }

.contact-result-list { display: flex; flex-direction: column; gap: 5px; }
.contact-result-btn {
  width: 100%; text-align: left;
  padding: 7px 12px; border-radius: 8px; border: 1.5px solid #e2e8f0;
  background: #f8fafc; font-size: 12px; font-weight: 500; color: #475569;
  cursor: pointer; transition: all 0.12s;
}
.contact-result-btn:hover { border-color: #c7d2fe; background: #eef2ff; }
.cr-no_answer.active  { background: #fff7ed; border-color: #fdba74; color: #9a3412; }
.cr-thinking.active   { background: #fefce8; border-color: #fde047; color: #854d0e; }
.cr-refused.active    { background: #fff1f2; border-color: #fca5a5; color: #9f1239; }
.cr-confirmed.active  { background: #f0fdf4; border-color: #86efac; color: #166534; }

.log-contact-btn {
  width: 100%; margin-top: 8px;
  padding: 8px 14px; border-radius: 8px; border: none;
  background: #6366f1; color: #fff; font-size: 12px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 5px;
}
.log-contact-btn:hover:not(:disabled) { background: #4f46e5; }
.log-contact-btn:disabled { opacity: .5; cursor: not-allowed; }

.contact-history-item {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 6px 8px; border-radius: 7px; margin-bottom: 4px;
  font-size: 12px; background: #f8fafc;
}
.chi-no_answer  { background: #fff7ed; }
.chi-thinking   { background: #fefce8; }
.chi-refused    { background: #fff1f2; }
.chi-confirmed  { background: #f0fdf4; }
.chi-icon       { font-size: 14px; flex-shrink: 0; }
.chi-body       { flex: 1; display: flex; flex-direction: column; gap: 1px; }
.chi-label      { font-weight: 600; color: #1e293b; }
.chi-note       { color: #64748b; font-size: 11px; }
.chi-time       { font-size: 10px; color: #94a3b8; white-space: nowrap; flex-shrink: 0; }

/* ─── History ─────────────────────────────────────────────────────────────── */
.history-list { display: flex; flex-direction: column; gap: 6px; }
.history-item { display: flex; align-items: flex-start; gap: 8px; }
.h-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #6366f1; margin-top: 4px; flex-shrink: 0;
}
.h-body { display: flex; flex-direction: column; gap: 1px; }
.h-text { font-size: 13px; color: #1e293b; }
.h-time { font-size: 11px; color: #94a3b8; }
/* ─── КОМУНІКАЦІЯ REDESIGN ─── */
.comm-compact-block { display: flex; flex-direction: column; gap: 16px; }

.comm-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.comm-pill {
  height: 34px;
  padding: 0 12px;
  border-radius: 20px;
  border: 1px solid #E0E0FF;
  background: #fff;
  color: #3D3AA8;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.comm-pill:hover { border-color: #3D3AA8; background: #f8f9ff; }
.comm-pill.active { background: #3D3AA8; color: #fff; border-color: #3D3AA8; box-shadow: 0 4px 10px rgba(61, 58, 168, 0.2); }

.results-grid-2x2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.result-tile {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
  background: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

/* Status Specific Styles */
.result-tile.no_answer.active { background: #FEF2F2; color: #991B1B; border-color: #FCA5A5; }
.result-tile.thinking.active  { background: #FFFBEB; color: #92400E; border-color: #FCD34D; }
.result-tile.refused.active   { background: #F9FAFB; color: #374151; border-color: #D1D5DB; }
.result-tile.confirmed.active { background: #ECFDF5; color: #065F46; border-color: #6EE7B7; transform: scale(1.02); }

.reminder-bar {
  margin-top: 4px;
  padding: 8px 12px;
  background: rgba(61, 58, 168, 0.04);
  border: 1px dashed #3D3AA8;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.reminder-head { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 700; color: #3D3AA8; }
.bell-icon { font-size: 14px; }
.compact-picker { width: 140px !important; }
:deep(.compact-picker .el-input__wrapper) { background: transparent !important; box-shadow: none !important; }

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(-10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }

/* ─── Communication Timeline ─── */
.comm-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  padding-left: 20px;
}
.comm-timeline::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 5px;
  bottom: 5px;
  width: 2px;
  background: #f1f5f9;
}
.timeline-item {
  position: relative;
}
.timeline-dot {
  position: absolute;
  left: -20px;
  top: 6px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid #fff;
  z-index: 1;
}
.timeline-content {
  background: #f8fafc;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
}
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.timeline-channel {
  font-size: 11px;
  font-weight: 700;
  color: #3D3AA8;
}
.timeline-time {
  font-size: 10px;
  color: #94a3b8;
}
.timeline-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.timeline-res-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}
.timeline-manager {
  font-size: 11px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}
.timeline-note {
  font-size: 12px;
  color: #1e293b;
  line-height: 1.4;
}
.timeline-reminder {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
  font-size: 10px;
  color: #6366f1;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.field-error :deep(.el-input__wrapper),
.field-error.el-select :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #ef4444 inset !important;
}

/* ─── ORDER SUMMARY 2026 REDESIGN ─── */
.inline-edit-amounts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.inline-amount-box {
  display: flex;
  flex-direction: column;
}

.inline-amount-input {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  width: 100%;
  cursor: text;
  outline: none;
  padding-bottom: 4px;
  transition: border-color 0.2s ease;
}

.inline-amount-input.prepay {
  color: #3D3AA8;
}

.inline-amount-input:focus {
  border-bottom-color: #3D3AA8;
}

.inline-amount-input::-webkit-outer-spin-button,
.inline-amount-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.inline-amount-input {
  -moz-appearance: textfield;
}

.inline-amount-label {
  font-size: 12px;
  color: #6B7280;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.prepay-pct-hint {
  color: #3D3AA8;
  font-weight: 600;
}

.prepay-pills-new {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.pill-new {
  border-radius: 20px;
  padding: 5px 14px;
  border: 1.5px solid #E0E0FF;
  background: white;
  color: #3D3AA8;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-new:hover {
  background: #F5F3FF;
  border-color: #3D3AA8;
}

.pill-new.active {
  background: #3D3AA8;
  color: white;
  border-color: #3D3AA8;
}

.payment-badge-new {
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  width: 100%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.payment-badge-new.unpaid {
  background: #F9FAFB;
  color: #6B7280;
}
.payment-badge-new.unpaid .status-dot-new {
  background: #9CA3AF;
}

.payment-badge-new.partial {
  background: #FFFBEB;
  color: #92400E;
}
.payment-badge-new.partial .status-dot-new {
  background: #F59E0B;
}

.payment-badge-new.paid {
  background: #ECFDF5;
  color: #065F46;
}
.payment-badge-new.paid .status-dot-new {
  background: #10B981;
}

.status-dot-new {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.modern-select :deep(.el-input__wrapper) {
  border-radius: 10px;
  border: 1px solid #E8EAFF;
  box-shadow: none !important;
}

.modern-select :deep(.el-input__wrapper.is-focus) {
  border-color: #3D3AA8;
}

.crm-date-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #475569;
  margin-top: 16px;
}

.date-val {
  font-weight: 600;
  color: #1E293B;
}

.date-val.blue {
  color: #3D3AA8;
}

.date-val.gray {
  color: #9CA3AF;
}

/* Keep existing styles below... */
</style>
