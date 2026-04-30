export const createInitialCrmOrderForm = (stage = 'new') => ({
  order_number: 'Авто',
  order_date: new Date().toISOString().slice(0, 10),
  counterparty_id: null,
  warehouse_id: null,
  product_id: null,
  crm_stage: stage,
  lead_source_id: null,
  channel: null,
  city: null,
  delivery_type: null,
  attributes_values: {},
  total_amount: 0,
  paid_amount: 0,
  payment_status: 'unpaid',
  prepayment_percent: null,
  prepayment_amount: null,
  deadline_date: null,
  next_contact_date: null,
  priority: 'normal',
  manager_id: null,
  comment: null,
  internal_notes: null,
  reference_photo: null,
  discount_percent: 0,
  np_branch: null,
  next_contact_at: null,
  next_contact_channel: 'CALL',
  next_contact_comment: null,
  contact_attempts: 0,
})

export const createNewClientForm = () => ({
  name: '',
  phone: '',
  email: '',
})

export const createMaterialCheckState = () => ({
  has_issues: false,
  items: [],
})
