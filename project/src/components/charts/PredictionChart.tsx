import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface PredictionData {
  time: string
  probability: number
}

interface PredictionChartProps {
  data: PredictionData[]
}

export function PredictionChart({ data }: PredictionChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>30-Minute Availability Prediction</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[0, 1]} tickFormatter={(value: number) => `${(value * 100).toFixed(0)}%`} />
              <Tooltip
                formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Availability']}
                labelFormatter={(label: string | number) => `Time: ${label}`}
              />
              <Line
                type="monotone"
                dataKey="probability"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}