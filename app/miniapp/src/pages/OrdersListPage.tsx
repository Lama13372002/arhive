import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useOrderStore } from '@/stores/orderStore'
import { useToast } from '@/hooks/use-toast'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function OrdersListPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { toast } = useToast()
  const { orders, fetchOrders, isLoading } = useOrderStore()
  
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    fetchOrders({ status: statusFilter === 'all' ? undefined : statusFilter })
  }, [statusFilter, fetchOrders])

  const filteredOrders = orders.filter(order => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      return (
        order.recipient?.toLowerCase().includes(searchLower) ||
        order.occasion?.toLowerCase().includes(searchLower) ||
        order.genre?.toLowerCase().includes(searchLower)
      )
    }
    return true
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800'
      case 'pending_lyrics': return 'bg-blue-100 text-blue-800'
      case 'lyrics_ready': return 'bg-green-100 text-green-800'
      case 'user_editing': return 'bg-yellow-100 text-yellow-800'
      case 'approved': return 'bg-purple-100 text-purple-800'
      case 'generating': return 'bg-orange-100 text-orange-800'
      case 'delivered': return 'bg-green-100 text-green-800'
      case 'canceled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  if (isLoading && orders.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">{t('orders.title')}</h1>
          <Button onClick={() => navigate('/create')}>
            <Plus className="w-4 h-4 mr-2" />
            {t('orders.create_first')}
          </Button>
        </div>

        {/* Search and filters */}
        <div className="mb-6 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <input
              type="text"
              placeholder={t('orders.search')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background"
            />
          </div>

          <div className="flex gap-2 overflow-x-auto">
            {[
              { key: 'all', label: t('orders.filter.all') },
              { key: 'draft', label: t('orders.filter.draft') },
              { key: 'pending', label: t('orders.filter.pending') },
              { key: 'ready', label: t('orders.filter.ready') }
            ].map((filter) => (
              <Button
                key={filter.key}
                variant={statusFilter === filter.key ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter(filter.key)}
              >
                {filter.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Orders list */}
        {filteredOrders.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-muted-foreground mb-4">
                {searchTerm || statusFilter !== 'all' 
                  ? 'Заказы не найдены' 
                  : t('orders.empty')
                }
              </div>
              {!searchTerm && statusFilter === 'all' && (
                <Button onClick={() => navigate('/create')}>
                  {t('orders.create_first')}
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <Card 
                key={order.id} 
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate(`/orders/${order.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">
                        {order.recipient ? `Песня для ${order.recipient}` : 'Новая песня'}
                      </CardTitle>
                      <CardDescription className="mt-1">
                        {order.occasion && t(`create.occasion.occasions.${order.occasion}`)}
                        {order.genre && ` • ${t(`create.style.genres.${order.genre}`)}`}
                      </CardDescription>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                      {t(`order.status.${order.status}`)}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>{formatDate(order.created_at)}</span>
                    {order.lyrics_versions.length > 0 && (
                      <span>{order.lyrics_versions.length} версий текста</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Loading indicator for pagination */}
        {isLoading && orders.length > 0 && (
          <div className="flex justify-center mt-6">
            <LoadingSpinner />
          </div>
        )}
      </div>
    </div>
  )
}

