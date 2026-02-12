<template>
  <div class="ai-assistant-container">
    <!-- Floating AI Button -->
    <el-button
      v-if="!isOpen"
      class="ai-floating-button"
      type="primary"
      circle
      size="large"
      @click="toggleChat"
    >
      <el-icon :size="28"><Robot /></el-icon>
    </el-button>

    <!-- Chat Panel -->
    <transition name="slide-up">
      <div v-if="isOpen" class="ai-chat-panel">
        <!-- Header -->
        <div class="ai-chat-header">
          <div class="header-content">
            <el-icon :size="24" style="margin-right: 8px"><Robot /></el-icon>
            <span class="header-title">Kimi AI Асистент</span>
          </div>
          <div class="header-actions">
            <el-button text @click="clearHistory" style="color: white">
              <el-icon><Delete /></el-icon>
            </el-button>
            <el-button text @click="toggleChat" style="color: white">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- Status Banner (if AI not available) -->
        <el-alert
          v-if="!aiEnabled"
          type="warning"
          :closable="false"
          class="ai-status-alert"
        >
          {{ statusMessage }}
        </el-alert>

        <!-- Welcome Message -->
        <div v-if="messages.length === 0" class="welcome-message">
          <el-icon :size="48" class="welcome-icon"><MagicStick /></el-icon>
          <h3>Вітаю! 👋</h3>
          <p>Я ваш AI асистент. Можу допомогти з:</p>
          <ul>
            <li>📊 Аналізом продажів та даних</li>
            <li>💡 Порадами щодо бізнесу</li>
            <li>📝 Генерацією описів товарів</li>
            <li>❓ Відповідями на запитання</li>
          </ul>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer" class="ai-chat-messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message-wrapper', msg.role === 'user' ? 'message-user-wrapper' : 'message-ai-wrapper']"
          >
            <div :class="['message-bubble', msg.role === 'user' ? 'message-user' : 'message-ai']">
              <div class="message-content" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ msg.time }}</div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="loading" class="message-wrapper message-ai-wrapper">
            <div class="message-bubble message-ai typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="ai-chat-input">
          <el-input
            v-model="currentMessage"
            :disabled="!aiEnabled || loading"
            placeholder="Введіть запит..."
            @keyup.enter="sendMessage"
            clearable
          >
            <template #append>
              <el-button 
                :icon="Position" 
                :loading="loading"
                :disabled="!aiEnabled || !currentMessage.trim()"
                @click="sendMessage"
              />
            </template>
          </el-input>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useKimiApi } from '@/composables/useKimiApi'

// Import Element Plus icons
import { 
  ChatDotRound as Robot,
  Close, 
  Delete, 
  Position,
  MagicStick 
} from '@element-plus/icons-vue'

const { loading, checkStatus, sendMessage: sendApiMessage } = useKimiApi()

const isOpen = ref(false)
const aiEnabled = ref(false)
const statusMessage = ref('Перевірка доступності AI...')
const currentMessage = ref('')
const messages = ref([])
const messagesContainer = ref(null)

// Check AI status on mount
onMounted(async () => {
  const status = await checkStatus()
  aiEnabled.value = status.enabled
  statusMessage.value = status.message
})

// Toggle chat panel
const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// Clear conversation history
const clearHistory = () => {
  messages.value = []
  ElMessage.success('Історію очищено')
}

// Send message to AI
const sendMessage = async () => {
  if (!currentMessage.value.trim() || !aiEnabled.value) return

  const userMessage = currentMessage.value.trim()
  const timestamp = new Date().toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })

  // Add user message
  messages.value.push({
    role: 'user',
    content: userMessage,
    time: timestamp
  })

  currentMessage.value = ''
  scrollToBottom()

  try {
    // Prepare conversation history for context
    const conversationHistory = messages.value
      .slice(0, -1) // Exclude the message we just added
      .map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content
      }))

    // Get current page context
    const context = `Користувач на сторінці: ${getCurrentPageContext()}`

    // Send to AI
    const response = await sendApiMessage(userMessage, context, conversationHistory)

    // Add AI response
    messages.value.push({
      role: 'assistant',
      content: response.response,
      time: new Date().toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
    })

    scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    // Remove the user message if there was an error
    messages.value.pop()
  }
}

// Get current page context from route
const getCurrentPageContext = () => {
  const path = window.location.pathname
  if (path.includes('dashboard')) return 'Dashboard'
  if (path.includes('inventory')) return 'Склад'
  if (path.includes('sales')) return 'Продажі'
  if (path.includes('purchases')) return 'Закупівлі'
  if (path.includes('finance')) return 'Фінанси'
  return 'Головна сторінка'
}

// Format message content (simple markdown-like formatting)
const formatMessage = (content) => {
  // Convert newlines to <br>
  let formatted = content.replace(/\n/g, '<br>')
  
  // Convert **bold**
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  
  // Convert numbered lists
  formatted = formatted.replace(/^(\d+)\.\s/gm, '<br>$1. ')
  
  // Convert bullet points
  formatted = formatted.replace(/^[•-]\s/gm, '<br>• ')
  
  return formatted
}

// Auto-scroll to bottom
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Watch messages and scroll
watch(() => messages.value.length, () => {
  scrollToBottom()
})
</script>

<style scoped>
.ai-assistant-container {
  position: fixed;
  z-index: 2000;
}

/* Floating Button */
.ai-floating-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  border: none;
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
  transition: all 0.3s;
}

.ai-floating-button:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 28px rgba(139, 92, 246, 0.5);
}

/* Chat Panel */
.ai-chat-panel {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.ai-chat-header {
  background: linear-gradient(135deg, #9333ea 0%, #c026d3 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 4px;
}

/* Status Alert */
.ai-status-alert {
  margin: 12px;
  border-radius: 8px;
}

/* Welcome Message */
.welcome-message {
  padding: 40px 24px;
  text-align: center;
  color: #64748b;
}

.welcome-icon {
  color: #9333ea;
  margin-bottom: 16px;
}

.welcome-message h3 {
  margin: 8px 0 16px 0;
  color: #1e293b;
}

.welcome-message ul {
  text-align: left;
  list-style: none;
  padding: 0;
  margin: 16px auto 0 auto;
  max-width: 280px;
}

.welcome-message li {
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.welcome-message li:last-child {
  border-bottom: none;
}

/* Messages Area */
.ai-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
}

.message-wrapper {
  display: flex;
  margin-bottom: 12px;
}

.message-user-wrapper {
  justify-content: flex-end;
}

.message-ai-wrapper {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 16px;
  position: relative;
}

.message-user {
  background: #dbeafe;
  border-radius: 16px 16px 4px 16px;
  color: #1e293b;
}

.message-ai {
  background: white;
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  color: #1e293b;
}

.message-content {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  text-align: right;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9333ea;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* Input Area */
.ai-chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e2e8f0;
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .ai-chat-panel {
    width: calc(100vw - 32px);
    height: calc(100vh - 120px);
    right: 16px;
    bottom: 80px;
  }

  .ai-floating-button {
    right: 16px;
  }
}
</style>
