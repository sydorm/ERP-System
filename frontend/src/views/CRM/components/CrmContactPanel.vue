<template>
    <div class="crm-section control-card next-touch-card">
      <div class="side-card-title">
        <span>НАСТУПНИЙ КОНТАКТ</span>
        <b>{{ form.next_contact_at ? 'заплановано' : 'не задано' }}</b>
      </div>

      <div class="next-touch-grid">
        <el-select v-model="contactCommTypeModel" placeholder="Канал" size="small">
          <el-option v-for="ct in communicationTypes" :key="ct.code" :label="`${ct.icon} ${ct.name}`" :value="ct.code" />
        </el-select>
        <el-select v-model="contactPlanReasonModel" placeholder="Причина" size="small">
          <el-option label="Перший контакт" value="first_touch" />
          <el-option label="Повтор після не відповів" value="retry_no_answer" />
          <el-option label="Уточнити деталі" value="clarify" />
          <el-option label="Нагадати про оплату" value="payment" />
          <el-option label="Погодити виробництво" value="production" />
        </el-select>
      </div>

      <el-date-picker
        v-model="form.next_contact_at"
        type="datetime"
        format="DD.MM.YYYY HH:mm"
        value-format="YYYY-MM-DDTHH:mm:ss"
        placeholder="Дата і час контакту"
        style="width: 100%; margin-top: 8px;"
      />

      <el-input
        v-model="form.next_contact_comment"
        class="next-contact-comment"
        type="textarea"
        :rows="2"
        placeholder="Коротко: що зробити під час наступного контакту..."
      />

      <div class="quick-touch-buttons">
        <button @click="$emit('set-next-contact-preset', { minutes: 15, reason: 'first_touch' })">+15 хв</button>
        <button @click="$emit('set-next-contact-preset', { hours: 2, reason: 'retry_no_answer' })">+2 год</button>
        <button @click="$emit('set-next-contact-preset', { tomorrow: true, h: 10, reason: 'clarify' })">Завтра 10:00</button>
        <button @click="$emit('set-next-contact-preset', { days: 2, h: 10, reason: 'payment' })">+2 дні</button>
      </div>

      <div class="next-touch-summary" :class="{ empty: !form.next_contact_at }">
        {{ nextTouchSummary }}
      </div>
    </div>

    <div class="crm-section" style="background: white; border: 1px solid #EBEBEB; border-radius: 12px; padding: 16px;">
      <el-button type="primary" :icon="UserIcon" style="width: 100%; font-weight: 600; border-radius: 8px;" @click="$emit('open-communication')">
        💬 Швидкий контакт (Комунікація)
      </el-button>
    </div>

    <div class="crm-section control-card">
      <div class="contact-script-panel">
        <div class="script-panel-title">Результат контакту</div>
        <button
          v-for="cr in contactResults"
          :key="cr.code"
          class="result-card"
          :class="[contactResult === cr.code ? 'active' : '', `result-${cr.code.toLowerCase()}`]"
          @click="$emit('apply-contact-result', cr.code)"
          type="button"
        >
          <strong>{{ cr.name }}</strong>
          <small>{{ getResultHint(cr.code) }}</small>
        </button>
      </div>

      <Transition name="fade-slide">
        <div v-if="['THINKING', 'NO_ANSWER'].includes(contactResult)" class="followup-box">
          <div class="followup-head">
            <strong>Повторний дотик</strong>
            <span>{{ contactResult === 'NO_ANSWER' ? 'клієнт не відповів' : 'клієнт думає' }}</span>
          </div>
          <el-date-picker
            v-model="contactNextAtModel"
            type="datetime"
            size="small"
            format="DD.MM HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="Дата/час контакту"
            style="width: 100%;"
          />
          <div class="contact-preset-row">
            <button @click="$emit('set-next-contact-preset', { hours: 2, reason: 'retry_no_answer', syncContactLog: true })">+2 год</button>
            <button @click="$emit('set-next-contact-preset', { tomorrow: true, h: 10, reason: 'clarify', syncContactLog: true })">Завтра 10:00</button>
            <button @click="$emit('set-next-contact-preset', { days: 2, h: 10, reason: 'clarify', syncContactLog: true })">+2 дні</button>
          </div>
        </div>
      </Transition>

      <div class="crm-field contact-note-field">
        <label class="crm-label">{{ contactResult === 'REFUSED' ? 'Причина відмови' : 'Нотатка контакту' }}</label>
        <el-input
          v-model="contactNoteModel"
          type="textarea"
          :rows="2"
          :placeholder="contactResult === 'REFUSED' ? 'Чому клієнт відмовився...' : 'Що сказав клієнт, домовленості, нюанси...'"
        />
      </div>

      <button class="save-contact-action" @click="$emit('log-contact')" :disabled="!contactResult || savingContact || !orderId">
        <el-icon v-if="savingContact" class="is-loading"><Loading /></el-icon>
        {{ orderId ? 'Зафіксувати контакт' : 'Збережіть заявку спочатку' }}
      </button>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loading, User as UserIcon } from '@element-plus/icons-vue'

const props = defineProps({
  form: { type: Object, required: true },
  orderId: { type: [String, Number, null], default: null },
  communicationTypes: { type: Array, required: true },
  contactResults: { type: Array, required: true },
  contactResult: { type: String, default: null },
  contactCommType: { type: String, default: 'CALL' },
  contactPlanReason: { type: String, default: 'first_touch' },
  contactNextAt: { type: String, default: null },
  contactNote: { type: String, default: '' },
  nextTouchSummary: { type: String, required: true },
  savingContact: { type: Boolean, default: false },
  getResultHint: { type: Function, required: true },
})

const emit = defineEmits([
  'update:contactCommType',
  'update:contactPlanReason',
  'update:contactNextAt',
  'update:contactNote',
  'set-next-contact-preset',
  'open-communication',
  'apply-contact-result',
  'log-contact',
])

const contactCommTypeModel = computed({ get: () => props.contactCommType, set: v => emit('update:contactCommType', v) })
const contactPlanReasonModel = computed({ get: () => props.contactPlanReason, set: v => emit('update:contactPlanReason', v) })
const contactNextAtModel = computed({ get: () => props.contactNextAt, set: v => emit('update:contactNextAt', v) })
const contactNoteModel = computed({ get: () => props.contactNote, set: v => emit('update:contactNote', v) })
</script>



