import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { useAuthStore } from '@/stores/authStore'
import { useEffect } from 'react'

// Pages
import WelcomePage from '@/pages/WelcomePage'
import CreateOrderPage from '@/pages/CreateOrderPage'
import OrderDetailsPage from '@/pages/OrderDetailsPage'
import OrdersListPage from '@/pages/OrdersListPage'
import ProfilePage from '@/pages/ProfilePage'

// Components
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorBoundary from '@/components/ErrorBoundary'

function App() {
  const { initAuth, isLoading } = useAuthStore()

  useEffect(() => {
    initAuth()
  }, [initAuth])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background text-foreground">
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/create" element={<CreateOrderPage />} />
          <Route path="/orders" element={<OrdersListPage />} />
          <Route path="/orders/:id" element={<OrderDetailsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
        <Toaster />
      </div>
    </ErrorBoundary>
  )
}

export default App

