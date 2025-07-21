import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend,
  className 
}) => {
  return (
    <div className={`stat-card ${className || ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-secondary mb-1">
            {title}
          </p>
          <p className="text-3xl font-bold text-primary mb-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {subtitle && (
            <p className="text-sm text-muted">
              {subtitle}
            </p>
          )}
          {trend && (
            <div className="flex items-center mt-2">
              <div className={`flex items-center text-sm font-medium ${
                trend.isPositive 
                  ? 'text-success' 
                  : 'text-error'
              }`}>
                <span className="mr-1">
                  {trend.isPositive ? '↗' : '↘'}
                </span>
                {Math.abs(trend.value)}%
              </div>
            </div>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 stat-icon">
            <div className="text-accent">
              {icon}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard; 