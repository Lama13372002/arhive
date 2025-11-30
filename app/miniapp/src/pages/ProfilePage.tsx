import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, User, Bell, Globe, Info, MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/authStore'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { user } = useAuthStore()

  const handleLanguageChange = (language: 'ru' | 'kz' | 'en') => {
    // In a real app, this would update the user's language preference
    console.log('Language changed to:', language)
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
          
          <h1 className="text-2xl font-bold">{t('profile.title')}</h1>
        </div>

        {/* User info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Информация о пользователе
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-muted-foreground">Имя:</span>
                <span className="ml-2 font-medium">
                  {user?.first_name} {user?.last_name}
                </span>
              </div>
              {user?.username && (
                <div>
                  <span className="text-sm text-muted-foreground">Username:</span>
                  <span className="ml-2 font-medium">@{user.username}</span>
                </div>
              )}
              <div>
                <span className="text-sm text-muted-foreground">Telegram ID:</span>
                <span className="ml-2 font-medium">{user?.telegram_id}</span>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Дата регистрации:</span>
                <span className="ml-2 font-medium">
                  {user?.created_at && new Date(user.created_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Settings */}
        <div className="space-y-6">
          {/* Language */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Globe className="w-5 h-5 mr-2" />
                {t('profile.language')}
              </CardTitle>
              <CardDescription>
                Выберите язык интерфейса
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-2">
                {[
                  { key: 'ru', label: 'Русский', flag: '🇷🇺' },
                  { key: 'kz', label: 'Қазақша', flag: '🇰🇿' },
                  { key: 'en', label: 'English', flag: '🇺🇸' }
                ].map((lang) => (
                  <Button
                    key={lang.key}
                    variant={user?.locale === lang.key ? 'default' : 'outline'}
                    onClick={() => handleLanguageChange(lang.key as 'ru' | 'kz' | 'en')}
                    className="justify-start"
                  >
                    <span className="mr-2">{lang.flag}</span>
                    {lang.label}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Bell className="w-5 h-5 mr-2" />
                {t('profile.notifications')}
              </CardTitle>
              <CardDescription>
                Настройки уведомлений
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Уведомления о готовности заказов</span>
                  <Button size="sm" variant="outline">
                    Включено
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Уведомления о новых функциях</span>
                  <Button size="sm" variant="outline">
                    Включено
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* About */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Info className="w-5 h-5 mr-2" />
                {t('profile.about')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Версия приложения:</span>
                  <span className="ml-2">1.0.0</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Разработчик:</span>
                  <span className="ml-2">Sunog Team</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Описание:</span>
                  <span className="ml-2">AI генератор персональных песен</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Support */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageCircle className="w-5 h-5 mr-2" />
                {t('profile.support')}
              </CardTitle>
              <CardDescription>
                Нужна помощь? Свяжитесь с нами
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <MessageCircle className="w-4 h-4 mr-2" />
                  Написать в поддержку
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Info className="w-4 h-4 mr-2" />
                  FAQ и документация
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

