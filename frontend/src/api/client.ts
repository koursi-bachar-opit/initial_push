import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type { 
  Booking, 
  Machine, 
  MachineListing, 
  ServerMetric,
  LiveMetricsData,
  ApiResponse,
  PaginatedResponse 
} from '../types';

// Create axios instance with base URL and auth headers
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login if token is invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Type-safe API functions
export const api = {
  // Listings
  getListings: (): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => 
    apiClient.get('/listings'),

  getFeaturedListings: (): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => 
    apiClient.get('/listings/featured'),

  searchListings: (searchTerm: string): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => 
    apiClient.get(`/listings/search?name=${encodeURIComponent(searchTerm)}`),

  // Machines
  getMachines: (): Promise<AxiosResponse<ApiResponse<Machine[]>>> => 
    apiClient.get('/machines'),

  getMachineMetrics: (machineId: string, params?: {
    start?: string;
    end?: string;
    limit?: number;
  }): Promise<AxiosResponse<ApiResponse<ServerMetric[]>>> => 
    apiClient.get(`/metrics/machines/${machineId}`, { params }),

  // Bookings
  getBookings: (): Promise<AxiosResponse<ApiResponse<Booking[]>>> => 
    apiClient.get('/bookings'),

  getBookingStatus: (bookingId: string): Promise<AxiosResponse<ApiResponse<Booking>>> => 
    apiClient.get(`/bookings/${bookingId}`),

  // Live metrics dashboard
  getLiveMetrics: (machineId?: string): Promise<AxiosResponse<ApiResponse<LiveMetricsData>>> => {
    const endpoint = machineId ? `/metrics/live/${machineId}` : '/metrics/live';
    return apiClient.get(endpoint);
  },

  // Featured machines for comparison
  getFeaturedMachines: (): Promise<AxiosResponse<ApiResponse<Machine[]>>> => 
    apiClient.get('/machines/featured'),
};

export default apiClient;