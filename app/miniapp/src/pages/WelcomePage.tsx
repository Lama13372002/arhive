import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Music, Heart, Star, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/authStore'

export default function WelcomePage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { user } = useAuthStore()

  const features = [
    {
      icon: Music,
      title: t('welcome.features.ai.title'),
      description: t('welcome.features.ai.description'),
    },
    {
      icon: Heart,
      title: t('welcome.features.personal.title'),
      description: t('welcome.features.personal.description'),
    },
    {
      icon: Star,
      title: t('welcome.features.quality.title'),
      description: t('welcome.features.quality.description'),
    },
    {
      icon: Users,
      title: t('welcome.features.occasion.title'),
      description: t('welcome.features.occasion.description'),
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-background to-secondary/10">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-full mb-4">
            <Music className="w-8 h-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            {t('welcome.title')}
          </h1>
          <p className="text-muted-foreground text-lg">
            {t('welcome.subtitle')}
          </p>
          {user && (
            <p className="text-sm text-muted-foreground mt-2">
              {t('welcome.greeting', { name: user.first_name || t('common.friend') })}
            </p>
          )}
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {features.map((feature, index) => (
            <Card key={index} className="animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
              <CardHeader className="pb-3">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <feature.icon className="w-5 h-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="space-y-4">
          <Button
            size="lg"
            className="w-full h-14 text-lg font-semibold"
            onClick={() => navigate('/create')}
          >
            <Music className="w-5 h-5 mr-2" />
            {t('welcome.create_song')}
          </Button>

          <div className="grid grid-cols-2 gap-4">
            <Button
              variant="outline"
              size="lg"
              className="h-12"
              onClick={() => navigate('/orders')}
            >
              {t('welcome.my_orders')}
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="h-12"
              onClick={() => navigate('/profile')}
            >
              {t('welcome.profile')}
            </Button>
          </div>
        </div>

        {/* How it works */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-center">{t('welcome.how_it_works.title')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  step: 1,
                  title: t('welcome.how_it_works.step1.title'),
                  description: t('welcome.how_it_works.step1.description'),
                },
                {
                  step: 2,
                  title: t('welcome.how_it_works.step2.title'),
                  description: t('welcome.how_it_works.step2.description'),
                },
                {
                  step: 3,
                  title: t('welcome.how_it_works.step3.title'),
                  description: t('welcome.how_it_works.step3.description'),
                },
                {
                  step: 4,
                  title: t('welcome.how_it_works.step4.title'),
                  description: t('welcome.how_it_works.step4.description'),
                },
              ].map((item, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-semibold">
                    {item.step}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm mb-1">{item.title}</h4>
                    <p className="text-xs text-muted-foreground">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

