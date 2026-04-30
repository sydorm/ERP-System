export const defaultCommTypes = [
  { code: 'CALL', name: 'Телефон', icon: '📞' },
  { code: 'VIBER', name: 'Viber', icon: '💬' },
  { code: 'TELEGRAM', name: 'Telegram', icon: '✈️' },
  { code: 'INSTAGRAM', name: 'Instagram', icon: '📸' },
  { code: 'SMS', name: 'SMS', icon: '📱' },
  { code: 'EMAIL', name: 'Email', icon: '✉️' },
  { code: 'MEET', name: 'Зустріч', icon: '🤝' },
]

export const defaultContactResults = [
  { code: 'NO_ANSWER', name: 'Не відповів', icon: '🔴' },
  { code: 'THINKING', name: 'Думає', icon: '🤔' },
  { code: 'CLARIFY', name: 'Уточнює', icon: '🔍' },
  { code: 'REFUSED', name: 'Відмовився', icon: '✗' },
  { code: 'CONFIRMED', name: 'Підтвердив', icon: '✓' },
  { code: 'RETRY', name: 'Потрібен повторний дзвінок', icon: '⏳' },
  { code: 'FORWARD', name: 'Передати далі', icon: '➡️' },
]

export const messageTemplates = [
  { title: 'Нагадування про заявку', text: 'Доброго дня! Нагадуємо про вашу заявку. Чи актуально?' },
  { title: 'Погодження ціни', text: 'Ціна розрахована. Будь ласка, ознайомтеся та підтвердіть.' },
  { title: 'Уточнення розмірів', text: 'Для точного прорахунку потрібні габаритні розміри виробу.' },
  { title: 'Надішліть фото', text: 'Чекаємо на фото референсів від вас!' },
  { title: 'Підтвердження замовлення', text: 'Ваше замовлення успішно підтверджено та готове до запуску.' },
]

export const getCommShort = (code) => ({
  CALL: 'TEL',
  VIBER: 'VIB',
  TELEGRAM: 'TG',
  INSTAGRAM: 'IG',
  EMAIL: 'MAIL',
  MEET: 'MEET',
}[code] || String(code || '').slice(0, 4).toUpperCase())

export const getResultHint = (code) => ({
  NO_ANSWER: 'створити нагадування',
  THINKING: 'запланувати дотик',
  CLARIFY: 'уточнити деталі',
  REFUSED: 'зафіксувати причину',
  CONFIRMED: 'передати далі',
  RETRY: 'повторити спробу',
  FORWARD: 'передати наступному',
}[code] || 'записати результат')

export const toLocalDateTimeValue = (date) => {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}
