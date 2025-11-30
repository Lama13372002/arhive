import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useOrderStore } from '@/stores/orderStore'
import { useToast } from '@/hooks/use-toast'

export default function CreateOrderPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { toast } = useToast()
  const { createOrder, isLoading } = useOrderStore()
  
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    language: 'ru' as 'ru' | 'kz' | 'en',
    genre: '',
    mood: '',
    tempo: '',
    occasion: '',
    recipient: '',
    notes: ''
  })

  const totalSteps = 4

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    try {
      const order = await createOrder(formData)
      toast({
        title: t('success.order_created'),
        description: 'Переходим к редактированию текста...'
      })
      navigate(`/orders/${order.id}`)
    } catch (error: any) {
      toast({
        title: t('common.error'),
        description: error.message || 'Ошибка создания заказа',
        variant: 'destructive'
      })
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('create.language.title')}</h3>
            <p className="text-muted-foreground">{t('create.language.description')}</p>
            <div className="grid grid-cols-1 gap-3">
              {(['ru', 'kz', 'en'] as const).map((lang) => (
                <Button
                  key={lang}
                  variant={formData.language === lang ? 'default' : 'outline'}
                  onClick={() => setFormData(prev => ({ ...prev, language: lang }))}
                  className="justify-start"
                >
                  {t(`create.language.${lang}`)}
                </Button>
              ))}
            </div>
          </div>
        )
      
      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">{t('create.style.title')}</h3>
            <p className="text-muted-foreground">{t('create.style.description')}</p>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">{t('create.style.genre')}</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries({
                    pop: t('create.style.genres.pop'),
                    rock: t('create.style.genres.rock'),
                    'hip-hop': t('create.style.genres.hip-hop'),
                    indie: t('create.style.genres.indie'),
                    ballad: t('create.style.genres.ballad'),
                    folk: t('create.style.genres.folk')
                  }).map(([key, label]) => (
                    <Button
                      key={key}
                      variant={formData.genre === key ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFormData(prev => ({ ...prev, genre: key }))}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">{t('create.style.mood')}</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries({
                    romantic: t('create.style.moods.romantic'),
                    happy: t('create.style.moods.happy'),
                    sad: t('create.style.moods.sad'),
                    motivational: t('create.style.moods.motivational')
                  }).map(([key, label]) => (
                    <Button
                      key={key}
                      variant={formData.mood === key ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFormData(prev => ({ ...prev, mood: key }))}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">{t('create.style.tempo')}</label>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries({
                    slow: t('create.style.tempos.slow'),
                    medium: t('create.style.tempos.medium'),
                    fast: t('create.style.tempos.fast')
                  }).map(([key, label]) => (
                    <Button
                      key={key}
                      variant={formData.tempo === key ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFormData(prev => ({ ...prev, tempo: key }))}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('create.occasion.title')}</h3>
            <p className="text-muted-foreground">{t('create.occasion.description')}</p>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">{t('create.occasion.occasion')}</label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries({
                    birthday: t('create.occasion.occasions.birthday'),
                    anniversary: t('create.occasion.occasions.anniversary'),
                    wedding: t('create.occasion.occasions.wedding'),
                    valentine: t('create.occasion.occasions.valentine'),
                    graduation: t('create.occasion.occasions.graduation'),
                    other: t('create.occasion.occasions.other')
                  }).map(([key, label]) => (
                    <Button
                      key={key}
                      variant={formData.occasion === key ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFormData(prev => ({ ...prev, occasion: key }))}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">{t('create.occasion.recipient')}</label>
                <input
                  type="text"
                  value={formData.recipient}
                  onChange={(e) => setFormData(prev => ({ ...prev, recipient: e.target.value }))}
                  placeholder="Имя получателя"
                  className="w-full px-3 py-2 border border-input rounded-md bg-background"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">{t('create.occasion.notes')}</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder={t('create.occasion.notes_placeholder')}
                  rows={3}
                  className="w-full px-3 py-2 border border-input rounded-md bg-background resize-none"
                />
              </div>
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('create.preview.title')}</h3>
            <p className="text-muted-foreground">{t('create.preview.description')}</p>
            
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Данные заказа</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div><strong>Язык:</strong> {t(`create.language.${formData.language}`)}</div>
                <div><strong>Жанр:</strong> {formData.genre ? t(`create.style.genres.${formData.genre}`) : 'Не выбран'}</div>
                <div><strong>Настроение:</strong> {formData.mood ? t(`create.style.moods.${formData.mood}`) : 'Не выбрано'}</div>
                <div><strong>Темп:</strong> {formData.tempo ? t(`create.style.tempos.${formData.tempo}`) : 'Не выбран'}</div>
                <div><strong>Повод:</strong> {formData.occasion ? t(`create.occasion.occasions.${formData.occasion}`) : 'Не выбран'}</div>
                <div><strong>Получатель:</strong> {formData.recipient || 'Не указан'}</div>
                {formData.notes && <div><strong>Дополнительно:</strong> {formData.notes}</div>}
              </CardContent>
            </Card>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('common.back')}
          </Button>
          
          <div className="text-sm text-muted-foreground">
            {t('create.step', { current: currentStep, total: totalSteps })}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-xs text-muted-foreground mb-2">
            <span>Язык</span>
            <span>Стиль</span>
            <span>Повод</span>
            <span>Проверка</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Step content */}
        <Card className="mb-6">
          <CardContent className="p-6">
            {renderStep()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 1}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('common.previous')}
          </Button>

          {currentStep < totalSteps ? (
            <Button
              onClick={handleNext}
              disabled={!formData.language}
            >
              {t('common.next')}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={isLoading || !formData.language}
            >
              {isLoading ? t('common.loading') : t('create.preview.generate')}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

