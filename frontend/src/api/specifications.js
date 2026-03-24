import api from './index'

export const getProductSpecifications = async (productId) => {
    const response = await api.get(`/api/v1/products/${productId}/specifications`)
    return response.data
}

export const createProductSpecification = async (productId, data) => {
    const response = await api.post(`/api/v1/products/${productId}/specifications`, data)
    return response.data
}

export const updateProductSpecification = async (specId, data) => {
    const response = await api.put(`/api/v1/products/specifications/${specId}`, data)
    return response.data
}

export const deleteProductSpecification = async (specId) => {
    const response = await api.delete(`/api/v1/products/specifications/${specId}`)
    return response.data
}
