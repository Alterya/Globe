import React, { ReactNode } from 'react';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, className }) => {
  return (
    <div className={`card ${className || ''}`}>
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-primary mb-1">
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-secondary">
            {subtitle}
          </p>
        )}
      </div>
      <div className="chart-container">
        {children}
      </div>
    </div>
  );
};

export default ChartCard; 