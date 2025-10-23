import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Car, MapPin, Clock, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/hooks/useAuth'

export function Home() {
  const { user } = useAuth()

  const features = [
    {
      icon: MapPin,
      title: 'Real-time Monitoring',
      description: 'Track parking slot availability in real-time across multiple locations'
    },
    {
      icon: Clock,
      title: 'Smart Predictions',
      description: 'AI-powered predictions help you find parking before you arrive'
    },
    {
      icon: Shield,
      title: 'Secure Reservations',
      description: 'Reserve your spot in advance with guaranteed availability'
    }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-6"
      >
        <motion.div
          initial={{ scale: 0.5 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2 }}
          className="inline-flex items-center space-x-2 text-6xl"
        >
          <Car className="text-primary" />
          <span className="font-bold text-gray-900">SmartPark</span>
        </motion.div>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-xl text-gray-600 max-w-2xl mx-auto"
        >
          The intelligent parking solution that helps you find, reserve, and manage parking spots 
          with real-time availability and AI-powered predictions.
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="space-x-4"
        >
          {user ? (
            <Link to="/dashboard">
              <Button size="lg">Go to Dashboard</Button>
            </Link>
          ) : (
            <>
              <Link to="/register">
                <Button size="lg">Get Started</Button>
              </Link>
              <Link to="/login">
                <Button variant="outline" size="lg">Sign In</Button>
              </Link>
            </>
          )}
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="space-y-8"
      >
        <h2 className="text-3xl font-bold text-center text-gray-900">
          Why Choose SmartPark?
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2 }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow">
                <CardHeader className="text-center">
                  <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-center">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="bg-primary text-primary-foreground rounded-2xl p-12 text-center"
      >
        <h2 className="text-3xl font-bold mb-4">Ready to Park Smarter?</h2>
        <p className="text-xl opacity-90 mb-8">
          Join thousands of users who have revolutionized their parking experience.
        </p>
        {!user && (
          <Link to="/register">
            <Button size="lg" variant="secondary">
              Start Your Free Trial
            </Button>
          </Link>
        )}
      </motion.section>
    </div>
  )
}