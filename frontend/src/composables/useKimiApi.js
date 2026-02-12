/**
 * Kimi AI Composable
 * Provides methods to interact with Kimi AI backend
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// Backend API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useKimiApi() {
    const loading = ref(false)
    const error = ref(null)

    /**
     * Check if Kimi AI is enabled
     */
    const checkStatus = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/ai/status`)
            const data = await response.json()
            return data
        } catch (err) {
            console.error('Failed to check AI status:', err)
            return { enabled: false, message: 'Backend не доступний' }
        }
    }

    /**
     * Send a chat message to Kimi AI
     */
    const sendMessage = async (message, context = null, conversationHistory = null) => {
        loading.value = true
        error.value = null

        try {
            const response = await fetch(`${API_BASE}/api/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    context,
                    conversation_history: conversationHistory
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Помилка відправки повідомлення')
            }

            const data = await response.json()
            loading.value = false
            return data
        } catch (err) {
            loading.value = false
            error.value = err.message
            ElMessage.error(err.message)
            throw err
        }
    }

    /**
     * Generate product description
     */
    const generateDescription = async (productName, category = null, additionalInfo = null) => {
        loading.value = true
        error.value = null

        try {
            const response = await fetch(`${API_BASE}/api/ai/generate-description`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_name: productName,
                    category,
                    additional_info: additionalInfo
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Помилка генерації опису')
            }

            const data = await response.json()
            loading.value = false
            return data.description
        } catch (err) {
            loading.value = false
            error.value = err.message
            ElMessage.error(err.message)
            throw err
        }
    }

    /**
     * Analyze business data
     */
    const analyzeData = async (dataType, data, question = null) => {
        loading.value = true
        error.value = null

        try {
            const response = await fetch(`${API_BASE}/api/ai/analyze-data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    data_type: dataType,
                    data,
                    question
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Помилка аналізу даних')
            }

            const data = await response.json()
            loading.value = false
            return data.analysis
        } catch (err) {
            loading.value = false
            error.value = err.message
            ElMessage.error(err.message)
            throw err
        }
    }

    return {
        loading,
        error,
        checkStatus,
        sendMessage,
        generateDescription,
        analyzeData
    }
}
