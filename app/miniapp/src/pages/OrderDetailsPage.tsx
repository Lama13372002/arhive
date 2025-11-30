import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, Edit, Check, RotateCcw, Download, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useOrderStore } from '@/stores/orderStore'
import { useToast } from '@/hooks/use-toast'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function OrderDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { toast } = useToast()
  const { 
    currentOrder, 
    fetchOrder, 
    approveOrder, 
    generateLyrics, 
    submitLyricsEdit,
    generateAudio,
    isLoading 
  } = useOrderStore()
  
  const [isEditingLyrics, setIsEditingLyrics] = useState(false)
  const [editedLyrics, setEditedLyrics] = useState('')

  useEffect(() => {
    if (id) {
      fetchOrder(parseInt(id))
    }
  }, [id, fetchOrder])

  useEffect(() => {
    if (currentOrder?.lyrics_versions.length) {
      const latestLyrics = currentOrder.lyrics_versions[currentOrder.lyrics_versions.length - 1]
      setEditedLyrics(latestLyrics.text)
    }
  }, [currentOrder])

  if (isLoading && !currentOrder) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!currentOrder) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Заказ не найден</h2>
          <Button onClick={() => navigate('/orders')}>
            Вернуться к списку
          </Button>
        </div>
      </div>
    )
  }

  const handleGenerateLyrics = async () => {
    try {
      await generateLyrics(currentOrder.id)
      toast({
        title: t('success.lyrics_generated'),
        description: 'Генерация текста началась...'
      })
    } catch (error: any) {
      toast({
        title: t('common.error'),
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleRegenerateLyrics = async () => {
    try {
      await generateLyrics(currentOrder.id, true)
      toast({
        title: t('success.lyrics_generated'),
        description: 'Перегенерация текста началась...'
      })
    } catch (error: any) {
      toast({
        title: t('common.error'),
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleSaveLyricsEdit = async () => {
    try {
      await submitLyricsEdit(currentOrder.id, editedLyrics)
      setIsEditingLyrics(false)
      toast({
        title: t('success.lyrics_edited'),
        description: 'Текст песни обновлен'
      })
    } catch (error: any) {
      toast({
        title: t('common.error'),
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleApproveOrder = async () => {
    try {
      await approveOrder(currentOrder.id)
      toast({
        title: t('success.order_approved'),
        description: 'Заказ утвержден'
      })
    } catch (error: any) {
      toast({
        title: t('common.error'),
        description: error.message,
        variant: 'destructive'
      })
    }
  }

  const handleGenerateAudio = async () => {
    try {
      await generateAudio(currentOrder.id)
      toast({
        title: 'Генерация аудио',
        description: 'Начинаем создание аудио версии...'
      })
    } catch (error: any) {
      toast({
        title: t('common.error'),
        description: error.message,
        variant: 'destructive'
      })
    }
  }

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

  const latestLyrics = currentOrder.lyrics_versions[currentOrder.lyrics_versions.length - 1]

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/orders')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('common.back')}
          </Button>
          
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(currentOrder.status)}`}>
            {t(`order.status.${currentOrder.status}`)}
          </span>
        </div>

        {/* Order info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>
              {currentOrder.recipient ? `Песня для ${currentOrder.recipient}` : 'Новая песня'}
            </CardTitle>
            <CardDescription>
              {currentOrder.occasion && t(`create.occasion.occasions.${currentOrder.occasion}`)}
              {currentOrder.genre && ` • ${t(`create.style.genres.${currentOrder.genre}`)}`}
              {currentOrder.mood && ` • ${t(`create.style.moods.${currentOrder.mood}`)}`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Язык:</span>
                <span className="ml-2">{t(`create.language.${currentOrder.language}`)}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Создан:</span>
                <span className="ml-2">
                  {new Date(currentOrder.created_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
            {currentOrder.notes && (
              <div className="mt-4">
                <span className="text-muted-foreground text-sm">Дополнительно:</span>
                <p className="text-sm mt-1">{currentOrder.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Lyrics section */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{t('order.lyrics.title')}</CardTitle>
              <div className="flex gap-2">
                {currentOrder.status === 'draft' && (
                  <Button size="sm" onClick={handleGenerateLyrics} disabled={isLoading}>
                    {t('create.preview.generate')}
                  </Button>
                )}
                {latestLyrics && currentOrder.status === 'lyrics_ready' && (
                  <>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => setIsEditingLyrics(true)}
                    >
                      <Edit className="w-4 h-4 mr-1" />
                      {t('order.lyrics.edit')}
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={handleRegenerateLyrics}
                      disabled={isLoading}
                    >
                      <RotateCcw className="w-4 h-4 mr-1" />
                      {t('order.lyrics.regenerate')}
                    </Button>
                    <Button 
                      size="sm" 
                      onClick={handleApproveOrder}
                      disabled={isLoading}
                    >
                      <Check className="w-4 h-4 mr-1" />
                      {t('order.lyrics.approve')}
                    </Button>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {latestLyrics ? (
              <div className="space-y-4">
                {isEditingLyrics ? (
                  <div className="space-y-4">
                    <textarea
                      value={editedLyrics}
                      onChange={(e) => setEditedLyrics(e.target.value)}
                      placeholder={t('order.lyrics.edit_placeholder')}
                      rows={15}
                      className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none font-mono text-sm"
                    />
                    <div className="flex gap-2">
                      <Button size="sm" onClick={handleSaveLyricsEdit} disabled={isLoading}>
                        {t('common.save')}
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => setIsEditingLyrics(false)}
                      >
                        {t('common.cancel')}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-sm text-muted-foreground">
                      {t('order.lyrics.version', { version: latestLyrics.version })} • 
                      {new Date(latestLyrics.created_at).toLocaleString('ru-RU')}
                    </div>
                    <pre className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded-md">
                      {latestLyrics.text}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                {currentOrder.status === 'pending_lyrics' 
                  ? 'Генерируется текст песни...'
                  : 'Текст песни еще не создан'
                }
              </div>
            )}
          </CardContent>
        </Card>

        {/* Audio section */}
        {currentOrder.audio_assets.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>{t('order.audio.title')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {currentOrder.audio_assets.map((asset) => (
                  <div key={asset.id} className="flex items-center justify-between p-4 border rounded-md">
                    <div>
                      <div className="font-medium">
                        {asset.kind === 'preview' ? 'Превью' : 'Полная версия'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {t(`order.audio.${asset.status}`)}
                        {asset.duration_sec && ` • ${Math.round(asset.duration_sec)}с`}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {asset.status === 'ready' && asset.url && (
                        <>
                          <Button size="sm" variant="outline">
                            <Play className="w-4 h-4 mr-1" />
                            {t('order.audio.play')}
                          </Button>
                          <Button size="sm">
                            <Download className="w-4 h-4 mr-1" />
                            {t('order.audio.download')}
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Generate audio button */}
        {currentOrder.status === 'approved' && currentOrder.audio_assets.length === 0 && (
          <Card>
            <CardContent className="text-center py-8">
              <h3 className="font-semibold mb-2">{t('order.audio.title')}</h3>
              <p className="text-muted-foreground mb-4">
                Создать аудио версию песни
              </p>
              <Button onClick={handleGenerateAudio} disabled={isLoading}>
                {isLoading ? t('common.loading') : 'Создать аудио'}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

