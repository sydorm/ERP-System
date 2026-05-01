export const createCrmOrderValidationErrors = () => ({
  client: false,
  amount: false,
})

export const collectMissingProductionFields = ({ form, clientName, clientPhone, requiredAttributesFilled, contactResult }) => {
  const missing = []
  if (!form.counterparty_id && !clientName) missing.push('Клієнт не обраний')
  if (!clientPhone) missing.push('Телефон не вказаний')
  if (!form.product_id) missing.push('Виріб не обраний')
  if (!requiredAttributesFilled) missing.push('Характеристики не заповнені')
  if (Number(form.total_amount || 0) <= 0) missing.push('Сума не вказана')
  if (!form.deadline_date) missing.push('Дата готовності (дедлайн) не вказана')

  const deliveryNeeded = form.delivery_type && form.delivery_type !== 'none'
  if (deliveryNeeded && !form.delivery_method_id) missing.push('Спосіб доставки не обраний')

  // Contact result is not required for production stages anymore
  return missing
}

export const validateCrmOrderRequiredFields = ({ form, clientName }) => ({
  client: !form.counterparty_id && !clientName,
  amount: !form.total_amount || form.total_amount <= 0,
})
