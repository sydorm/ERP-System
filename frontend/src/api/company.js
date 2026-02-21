import api from './index'

export const getCompanies = async () => {
    const response = await api.get('/api/v1/companies')
    return response.data
}

export const createCompany = async (data) => {
    const { bank_accounts, ...payload } = data
    const response = await api.post('/api/v1/companies', payload)
    return response.data
}

export const updateCompanySettings = async (data) => {
    const { id, bank_accounts, ...payload } = data
    // Remove unneeded/unsupported fields to avoid sending them to backend
    if ('users' in payload) delete payload.users
    if ('warehouses' in payload) delete payload.warehouses
    if ('products' in payload) delete payload.products
    if ('counterparties' in payload) delete payload.counterparties

    const response = await api.put(`/api/v1/companies/${id}`, payload)
    return response.data
}

export const setDefaultCompany = async (id) => {
    const response = await api.patch(`/api/v1/companies/${id}/set-default`)
    return response.data
}

export const fetchOfficialTaxRates = async (id) => {
    const response = await api.get(`/api/v1/companies/${id}/fetch-tax-rates`)
    return response.data
}

export const fetchEdrpouData = async (code) => {
    // Simulated implementation for auto-fill demo
    await new Promise(resolve => setTimeout(resolve, 1500));
    if (code === '12345678') {
        return {
            name: 'ТОВ "Рога і Копита"',
            full_name: 'Товариство з обмеженою відповідальністю "Рога і Копита"',
            address: 'м. Київ, вул. Хрещатик, 1',
            director: 'Іванов Іван Іванович',
            kved: '62.01'
        }
    }
    return null;
}
