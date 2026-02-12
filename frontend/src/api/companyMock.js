/**
 * Mock API for Company Settings
 * Since the backend might not be fully ready/migrated, we use this for frontend dev.
 */

// Simulated database
let companyData = {
    id: '1',
    name: 'ТОВ "Рога і Копита"',
    full_name_uk: 'Товариство з обмеженою відповідальністю "Рога і Копита"',
    short_name_uk: 'ТОВ "Рога і Копита"',
    edrpou: '12345678',
    ipn: '123456789012',
    director_name: 'Іванов Іван Іванович',
    director_position: 'Директор',
    legal_address: 'м. Київ, вул. Хрещатик, 1',
    physical_address: 'м. Київ, вул. Хрещатик, 1',
    phone: '+380501234567',
    email: 'info@hornsandhooves.com',
    company_type: 'TOV',
    tax_group: 'GROUP_3',
    vat_payer: true,
    bank_accounts: [
        {
            id: '101',
            bank_name: 'ПриватБанк',
            mfo: '305299',
            iban: 'UA12305299000002600000000001',
            currency: 'UAH',
            is_primary: true
        }
    ]
}

export const getCompanySettings = async () => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));
    return companyData;
}

export const updateCompanySettings = async (data) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    companyData = { ...companyData, ...data };
    return companyData;
}

export const getCompanies = async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return [companyData];
}

export const createCompany = async (data) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    const newCompany = { ...companyData, ...data, id: Date.now().toString(), is_default: false };
    return newCompany;
}

export const setDefaultCompany = async (id) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    companyData.is_default = (companyData.id === id);
    return companyData;
}

export const fetchOfficialTaxRates = async (id) => {
    await new Promise(resolve => setTimeout(resolve, 1200));
    return {
        tax_amount_esv: "1760.00",
        tax_rate_single: "5%",
        military_tax_rate: "5%",
        last_tax_update: new Date().toLocaleString()
    };
}
