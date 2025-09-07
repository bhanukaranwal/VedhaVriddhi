import numeral from 'numeral';

// Number formatting utilities
export const formatNumber = (value: number | string | null | undefined, format = '0,0'): string => {
  if (value === null || value === undefined || value === '') return '-';
  return numeral(value).format(format);
};

export const formatCurrency = (
  value: number | string | null | undefined, 
  currency = 'INR', 
  decimals = 2
): string => {
  if (value === null || value === undefined || value === '') return '-';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (currency === 'INR') {
    return `₹${formatNumber(numValue, `0,0.${'0'.repeat(decimals)}`)}`;
  }
  
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(numValue);
};

export const formatPercentage = (
  value: number | string | null | undefined, 
  decimals = 2,
  includeSign = false
): string => {
  if (value === null || value === undefined || value === '') return '-';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  const formatted = formatNumber(numValue, `0,0.${'0'.repeat(decimals)}`);
  
  if (includeSign && numValue > 0) {
    return `+${formatted}%`;
  }
  
  return `${formatted}%`;
};

export const formatBasisPoints = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') return '-';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  return `${formatNumber(numValue)} bps`;
};

export const formatDuration = (value: number | string | null | undefined, unit = 'years'): string => {
  if (value === null || value === undefined || value === '') return '-';
  
  const formatted = formatNumber(value, '0,0.00');
  return `${formatted} ${unit}`;
};

// Date formatting utilities
export const formatDate = (
  date: string | Date | null | undefined, 
  format: 'short' | 'medium' | 'long' | 'time' | 'datetime' = 'medium'
): string => {
  if (!date) return '-';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) return '-';
  
  const options: Intl.DateTimeFormatOptions = {
    timeZone: 'Asia/Kolkata',
  };
  
  switch (format) {
    case 'short':
      options.dateStyle = 'short';
      break;
    case 'medium':
      options.dateStyle = 'medium';
      break;
    case 'long':
      options.dateStyle = 'long';
      break;
    case 'time':
      options.timeStyle = 'medium';
      break;
    case 'datetime':
      options.dateStyle = 'medium';
      options.timeStyle = 'short';
      break;
  }
  
  return new Intl.DateTimeFormat('en-IN', options).format(dateObj);
};

export const formatRelativeTime = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInMs = now.getTime() - dateObj.getTime();
  
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
  
  const seconds = Math.floor(diffInMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return rtf.format(-days, 'day');
  if (hours > 0) return rtf.format(-hours, 'hour');
  if (minutes > 0) return rtf.format(-minutes, 'minute');
  return rtf.format(-seconds, 'second');
};

// Bond-specific formatting
export const formatYield = (value: number | string | null | undefined): string => {
  return formatPercentage(value, 3);
};

export const formatPrice = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') return '-';
  return formatNumber(value, '0,0.0000');
};

export const formatISIN = (isin: string | null | undefined): string => {
  if (!isin) return '-';
  // Format ISIN as XXXXXXXXXXXX -> XXXX XXXX XXXX
  return isin.replace(/(.{4})/g, '$1 ').trim();
};

export const formatMaturity = (maturityDate: string | Date | null | undefined): string => {
  if (!maturityDate) return '-';
  
  const maturity = typeof maturityDate === 'string' ? new Date(maturityDate) : maturityDate;
  const today = new Date();
  
  const years = Math.floor((maturity.getTime() - today.getTime()) / (365.25 * 24 * 60 * 60 * 1000));
  const months = Math.floor(((maturity.getTime() - today.getTime()) % (365.25 * 24 * 60 * 60 * 1000)) / (30.44 * 24 * 60 * 60 * 1000));
  
  if (years > 0 && months > 0) {
    return `${years}Y ${months}M`;
  } else if (years > 0) {
    return `${years}Y`;
  } else if (months > 0) {
    return `${months}M`;
  } else {
    return 'Maturing';
  }
};

// Volume formatting
export const formatVolume = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') return '-';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (numValue >= 1e9) {
    return formatNumber(numValue / 1e9, '0,0.0') + 'B';
  } else if (numValue >= 1e6) {
    return formatNumber(numValue / 1e6, '0,0.0') + 'M';
  } else if (numValue >= 1e3) {
    return formatNumber(numValue / 1e3, '0,0.0') + 'K';
  }
  
  return formatNumber(numValue, '0,0');
};

// Order and trade formatting
export const formatOrderSide = (side: 'buy' | 'sell' | string): string => {
  return side.charAt(0).toUpperCase() + side.slice(1).toLowerCase();
};

export const formatOrderStatus = (status: string): string => {
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

export const formatOrderType = (type: string): string => {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

// Utility functions
export const abbreviateNumber = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') return '-';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (Math.abs(numValue) >= 1e12) {
    return formatNumber(numValue / 1e12, '0,0.0') + 'T';
  } else if (Math.abs(numValue) >= 1e9) {
    return formatNumber(numValue / 1e9, '0,0.0') + 'B';
  } else if (Math.abs(numValue) >= 1e6) {
    return formatNumber(numValue / 1e6, '0,0.0') + 'M';
  } else if (Math.abs(numValue) >= 1e3) {
    return formatNumber(numValue / 1e3, '0,0.0') + 'K';
  }
  
  return formatNumber(numValue);
};

export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Bytes';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${formatNumber(bytes / Math.pow(1024, i), '0,0.00')} ${sizes[i]}`;
};

// Color coding for values
export const getColorForChange = (value: number): 'success' | 'error' | 'text.primary' => {
  if (value > 0) return 'success';
  if (value < 0) return 'error';
  return 'text.primary';
};

export const getColorForYield = (yield: number, benchmark: number): 'success' | 'error' | 'warning' | 'text.primary' => {
  const spread = yield - benchmark;
  if (spread > 2) return 'error';
  if (spread > 1) return 'warning';
  if (spread < -1) return 'success';
  return 'text.primary';
};
