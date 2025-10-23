import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface OccupancyData {
  name: string
  value: number
  color: string
}

interface OccupancyChartProps {
  data: {
    free: number
    occupied: number
    reserved: number
  }
  showPieChart?: boolean
}

export function OccupancyChart({ data, showPieChart = true }: OccupancyChartProps) {
  const pieData: OccupancyData[] = [
    { name: 'Free', value: data.free, color: '#10B981' },
    { name: 'Occupied', value: data.occupied, color: '#EF4444' },
    { name: 'Reserved', value: data.reserved, color: '#F59E0B' },
  ]

  const barData = [
    { status: 'Free', count: data.free, fill: '#10B981' },
    { status: 'Occupied', count: data.occupied, fill: '#EF4444' },
    { status: 'Reserved', count: data.reserved, fill: '#F59E0B' },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Slot Occupancy</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            {showPieChart ? (
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            ) : (
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}