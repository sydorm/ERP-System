<template>
  <div v-if="contacts.length" style="margin-top:20px">
    <div class="crm-section-title" style="margin-bottom:12px">Історія комунікацій</div>
    <div class="comm-timeline">
      <div v-for="c in contacts" :key="c.id" class="timeline-item">
        <div class="timeline-dot" :style="{ background: getContactResultColor(c.result) }" />
        <div class="timeline-content">
          <div class="timeline-header">
            <span class="timeline-channel">{{ getCommIcon(c.communication_type) }} {{ getCommName(c.communication_type) }}</span>
            <span class="timeline-time">{{ formatDateTime(c.contacted_at) }}</span>
          </div>
          <div class="timeline-main">
            <span class="timeline-res-badge" :style="{ background: getContactResultColor(c.result) + '15', color: getContactResultColor(c.result) }">
              {{ contactResultLabel(c.result) }}
            </span>
            <span class="timeline-manager"><el-icon><UserIcon /></el-icon> {{ c.manager?.name || 'Менеджер' }}</span>
          </div>
          <div class="timeline-note" v-if="c.note">{{ c.note }}</div>
          <div class="timeline-reminder" v-if="c.next_contact_at">
            <el-icon><Clock /></el-icon> Нагадування: {{ formatDateTime(c.next_contact_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Clock, User as UserIcon } from '@element-plus/icons-vue'

defineProps({
  contacts: { type: Array, required: true },
  getContactResultColor: { type: Function, required: true },
  getCommIcon: { type: Function, required: true },
  getCommName: { type: Function, required: true },
  formatDateTime: { type: Function, required: true },
  contactResultLabel: { type: Function, required: true },
})
</script>
