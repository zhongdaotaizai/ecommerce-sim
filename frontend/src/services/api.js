import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
const BASE_URL = "http://localhost:8000/api";
const api = axios.create({ baseURL: BASE_URL, timeout: 15000 });
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      AsyncStorage.removeItem("token");
    }
    return Promise.reject(err);
  }
);
export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
  getMe: () => api.get("/auth/me"),
  openShop: (data) => api.post("/auth/open-shop", data),
  getShop: () => api.get("/auth/shop"),
  getUserProfile: (id) => api.get(`/auth/profile/${id}`),
};
export const productAPI = {
  list: (params) => api.get("/products", { params }),
  detail: (id) => api.get(`/products/${id}`),
  getCategories: (params) => api.get("/products/categories", { params }),
  getPriceHistory: (productId, skuId) => api.get(`/products/${productId}/price-history`, { params: { sku_id: skuId } }),
  create: (data) => api.post("/products", data),
  addSku: (productId, data) => api.post(`/products/${productId}/skus`, data),
  getMyProducts: () => api.get("/products/seller/products"),
};
export const cartAPI = {
  getCart: () => api.get("/cart"),
  add: (data) => api.post("/cart", data),
  remove: (id) => api.delete(`/cart/${id}`),
  updateQuantity: (id, quantity) => api.put(`/cart/${id}/quantity`, null, { params: { quantity } }),
};
export const orderAPI = {
  checkout: (data) => api.post("/orders/checkout", data),
  pay: (orderId) => api.post(`/orders/${orderId}/pay`),
  list: (status) => api.get("/orders", { params: { status } }),
  applyRefund: (orderId, data) => api.post(`/orders/${orderId}/refund`, data),
  createReview: (orderId, data) => api.post(`/orders/${orderId}/review`, data),
  getSellerOrders: () => api.get("/orders/seller"),
  handleRefund: (refundId, action) => api.post(`/orders/refund/${refundId}/handle`, null, { params: { action } }),
};
export const marketAPI = {
  getState: () => api.get("/market/state"),
  getOverview: (day) => api.get("/market/overview", { params: { day } }),
  getPriceHistory: (productId) => api.get(`/market/price-history/${productId}`),
  getDecisionLogs: (buyerId, limit) => api.get(`/market/decision-log/${buyerId}`, { params: { limit } }),
  getHotRankings: (rankType, day) => api.get("/market/hot-rankings", { params: { rank_type: rankType, day } }),
  getEvents: () => api.get("/market/events"),
  getVirtualUsers: () => api.get("/market/users/virtual"),
  getUserDecision: (userId) => api.get(`/market/user/${userId}/decision`),
  getOrderDecision: (orderId) => api.get(`/market/decision-log/order/${orderId}`),
};
export const simAPI = {
  triggerDay: () => api.post("/simulate/day"),
  getStatus: () => api.get("/simulate/status"),
  reset: () => api.post("/simulate/reset"),
  init: () => api.post("/simulate/init"),
};
export default api;
