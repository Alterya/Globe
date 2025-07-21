import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ChartData } from '../types';

interface BarChartWidgetProps {
  data: ChartData[];
  color?: string;
  maxBars?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="card" style={{ padding: '1rem', minWidth: '160px' }}>
        <p className="text-sm font-medium text-primary mb-2">
          {label}
        </p>
        <p className="text-sm text-secondary">
          Count: <span className="font-semibold text-accent">{data.value}</span>
        </p>
        {data.percentage && (
          <p className="text-sm text-secondary">
            Percentage: <span className="font-semibold">{data.percentage}%</span>
          </p>
        )}
      </div>
    );
  }
  return null;
};

const BarChartWidget: React.FC<BarChartWidgetProps> = ({ 
  data, 
  color = '#6366f1',
  maxBars = 10 
}) => {
  const chartData = data.slice(0, maxBars);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        margin={{
          top: 20,
          right: 30,
          left: 20,
          bottom: 60,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" style={{ opacity: 0.3 }} />
        <XAxis 
          dataKey="name" 
          angle={-45}
          textAnchor="end"
          height={80}
          interval={0}
          tick={{ fontSize: 12 }}
          className="text-secondary"
        />
        <YAxis 
          tick={{ fontSize: 12 }}
          className="text-secondary"
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar 
          dataKey="value" 
          fill={color}
          radius={[4, 4, 0, 0]}
          style={{ cursor: 'pointer' }}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default BarChartWidget; 