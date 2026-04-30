export const buildReadinessItems = ({ form, clientPhone, requiredAttributesFilled }) => [
  { key: 'client', label: 'Клієнт обраний', done: Boolean(form.counterparty_id) },
  { key: 'phone', label: 'Телефон вказаний', done: Boolean(clientPhone) },
  { key: 'product', label: 'Виріб обраний', done: Boolean(form.product_id) },
  { key: 'attrs', label: 'Характеристики заповнені', done: requiredAttributesFilled },
  { key: 'amount', label: 'Сума вказана', done: Number(form.total_amount || 0) > 0 },
  { key: 'deadline', label: 'Дата готовності вказана', done: Boolean(form.deadline_date) },
  {
    key: 'contact',
    label: 'Наступний контакт запланований',
    done: !['new', 'payment'].includes(form.crm_stage) || Boolean(form.next_contact_at),
  },
  { key: 'payment', label: 'Спосіб оплати заданий', done: Boolean(form.bank_account_id) },
]

export const calculateReadinessProgress = (items) => {
  if (!items.length) return 0
  const done = items.filter(item => item.done).length
  return Math.round((done / items.length) * 100)
}
