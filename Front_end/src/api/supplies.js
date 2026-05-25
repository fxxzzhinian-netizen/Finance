import request from './request'

export function listSupplies(params) {
  return request.get('/api/supplies', { params })
}

export function getSupply(id) {
  return request.get(`/api/supplies/${id}`)
}

export function createSupply(data) {
  return request.post('/api/supplies', data)
}

export function updateSupply(id, data) {
  return request.put(`/api/supplies/${id}`, data)
}

export function deleteSupply(id) {
  return request.delete(`/api/supplies/${id}`)
}

export function previewNextSupplySerial() {
  return request.get('/api/supplies/next-serial')
}

export function getSupplyQrInfo(id) {
  return request.get(`/api/supplies/${id}/qrcode-info`)
}

export function getPublicSupply(serialNumber) {
  return request.get(`/api/public/supplies/${encodeURIComponent(serialNumber)}`)
}
