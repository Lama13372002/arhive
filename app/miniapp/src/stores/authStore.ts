import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '@/lib/api'

export interface User {
  id: number
  telegram_id: number
  username?: string
  first_name?: string
  last_name?: string
  phone?: string
  locale: 'ru' | 'kz' | 'en'
  created_at: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

export interface AuthActions {
  initAuth: () => Promise<void>
  login: (initData: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  setToken: (token: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,

      // Actions
      initAuth: async () => {
        set({ isLoading: true, error: null })
        
        try {
          // Get init data from Telegram WebApp
          const initData = window.Telegram?.WebApp?.initData
          
          if (!initData) {
            throw new Error('No Telegram init data available')
          }

          // Verify authentication with backend
          const response = await apiClient.post('/auth/telegram/verify', {
            init_data: initData
          })

          const { access_token, user } = response.data

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })

          // Set authorization header for future requests
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        } catch (error: any) {
          console.error('Auth initialization failed:', error)
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Authentication failed'
          })
        }
      },

      login: async (initData: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await apiClient.post('/auth/telegram/verify', {
            init_data: initData
          })

          const { access_token, user } = response.data

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })

          // Set authorization header
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login failed'
          })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null
        })
        
        // Remove authorization header
        delete apiClient.defaults.headers.common['Authorization']
      },

      setUser: (user: User) => {
        set({ user })
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true })
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
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
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

