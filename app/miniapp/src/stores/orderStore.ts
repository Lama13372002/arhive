import { create } from 'zustand'
import { apiClient } from '@/lib/api'

export interface Order {
  id: number
  status: 'draft' | 'pending_lyrics' | 'lyrics_ready' | 'user_editing' | 'approved' | 'generating' | 'delivered' | 'canceled'
  language: 'ru' | 'kz' | 'en'
  genre?: string
  mood?: string
  tempo?: string
  occasion?: string
  recipient?: string
  notes?: string
  price?: number
  currency: string
  payment_status: 'none' | 'pending' | 'paid' | 'failed' | 'refunded'
  created_at: string
  updated_at: string
  lyrics_versions: LyricsVersion[]
  audio_assets: AudioAsset[]
}

export interface LyricsVersion {
  id: number
  version: number
  text: string
  status: 'draft' | 'ready' | 'rejected'
  created_at: string
}

export interface AudioAsset {
  id: number
  kind: 'preview' | 'full'
  url?: string
  duration_sec?: number
  status: 'queued' | 'generating' | 'ready' | 'failed'
  created_at: string
}

export interface OrderCreateData {
  language: 'ru' | 'kz' | 'en'
  genre?: string
  mood?: string
  tempo?: string
  occasion?: string
  recipient?: string
  notes?: string
}

export interface OrderState {
  orders: Order[]
  currentOrder: Order | null
  isLoading: boolean
  error: string | null
}

export interface OrderActions {
  // Orders list
  fetchOrders: (params?: { skip?: number; limit?: number; status?: string }) => Promise<void>
  createOrder: (data: OrderCreateData) => Promise<Order>
  updateOrder: (id: number, data: Partial<OrderCreateData>) => Promise<Order>
  
  // Order details
  fetchOrder: (id: number) => Promise<Order>
  approveOrder: (id: number) => Promise<void>
  
  // Lyrics
  generateLyrics: (id: number, regenerate?: boolean) => Promise<string>
  submitLyricsEdit: (id: number, text: string) => Promise<LyricsVersion>
  
  // Audio
  generateAudio: (id: number) => Promise<string>
  
  // Payments
  createPayment: (id: number) => Promise<any>
  
  // State management
  setCurrentOrder: (order: Order | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useOrderStore = create<OrderState & OrderActions>((set, get) => ({
  // State
  orders: [],
  currentOrder: null,
  isLoading: false,
  error: null,

  // Actions
  fetchOrders: async (params = {}) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.get('/orders', { params })
      const { items } = response.data
      
      set({ orders: items, isLoading: false })
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to fetch orders' 
      })
      throw error
    }
  },

  createOrder: async (data: OrderCreateData) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.post('/orders', data)
      const order = response.data
      
      set(state => ({
        orders: [order, ...state.orders],
        currentOrder: order,
        isLoading: false
      }))
      
      return order
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to create order' 
      })
      throw error
    }
  },

  updateOrder: async (id: number, data: Partial<OrderCreateData>) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.patch(`/orders/${id}`, data)
      const updatedOrder = response.data
      
      set(state => ({
        orders: state.orders.map(order => 
          order.id === id ? updatedOrder : order
        ),
        currentOrder: state.currentOrder?.id === id ? updatedOrder : state.currentOrder,
        isLoading: false
      }))
      
      return updatedOrder
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to update order' 
      })
      throw error
    }
  },

  fetchOrder: async (id: number) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.get(`/orders/${id}`)
      const order = response.data
      
      set({ 
        currentOrder: order,
        isLoading: false 
      })
      
      return order
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to fetch order' 
      })
      throw error
    }
  },

  approveOrder: async (id: number) => {
    set({ isLoading: true, error: null })
    
    try {
      await apiClient.post(`/orders/${id}/approve`)
      
      set(state => ({
        orders: state.orders.map(order => 
          order.id === id ? { ...order, status: 'approved' as const } : order
        ),
        currentOrder: state.currentOrder?.id === id 
          ? { ...state.currentOrder, status: 'approved' as const }
          : state.currentOrder,
        isLoading: false
      }))
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to approve order' 
      })
      throw error
    }
  },

  generateLyrics: async (id: number, regenerate = false) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.post(`/orders/${id}/lyrics/generate`, {
        regenerate
      })
      
      set({ isLoading: false })
      return response.data.task_id
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to generate lyrics' 
      })
      throw error
    }
  },

  submitLyricsEdit: async (id: number, text: string) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.post(`/orders/${id}/lyrics/submit_edit`, {
        text
      })
      
      const lyricsVersion = response.data
      
      set(state => ({
        currentOrder: state.currentOrder?.id === id 
          ? {
              ...state.currentOrder,
              lyrics_versions: [...state.currentOrder.lyrics_versions, lyricsVersion],
              status: 'lyrics_ready' as const
            }
          : state.currentOrder,
        isLoading: false
      }))
      
      return lyricsVersion
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to submit lyrics edit' 
      })
      throw error
    }
  },

  generateAudio: async (id: number) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.post(`/orders/${id}/generate_audio`)
      
      set({ isLoading: false })
      return response.data.task_id
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to generate audio' 
      })
      throw error
    }
  },

  createPayment: async (id: number) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.post(`/orders/${id}/pay`)
      
      set({ isLoading: false })
      return response.data
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to create payment' 
      })
      throw error
    }
  },

  setCurrentOrder: (order: Order | null) => {
    set({ currentOrder: order })
  },

  setLoading: (isLoading: boolean) => {
    set({ isLoading })
  },

  setError: (error: string | null) => {
    set({ error })
  },

  clearError: () => {
    set({ error: null })
  }
}))

