// frontend/src/components/Logo.tsx
import React, { useId } from 'react'; // 1. Импортируем хук useId

interface LogoProps {
  iconOnly?: boolean;
  width?: number;
}

export const Logo: React.FC<LogoProps> = ({ iconOnly = false, width }) => {
  // 2. Генерируем уникальные ID для этого экземпляра компонента
  const gradientId = useId();
  const shadowId = useId();

  const height = width ? width * (42 / (iconOnly ? 42 : 172)) : (iconOnly ? 42 : 40);

  const Icon = () => (
    // 3. Применяем уникальный ID к фильтру
    <g filter={`url(#${shadowId})`}>
      <path d="M2,10 C2,4.477 6.477,0 12,0 H30 C35.523,0 40,4.477 40,10 V28 C40,33.523 35.523,38 30,38 H12 C6.477,38 2,33.523 2,28 V10 Z" fill="#434190"/>
      <path d="M38,2 C32,2 15,18 15,30 C15,35 38,15 38,2 Z" fill="#000" opacity="0.2"/>
      {/* 4. И применяем уникальный ID к градиенту */}
      <path d="M38,2 C30,2 10,20 10,32 C10,38 40,15 40,8 V4 C40,2.895 39.105,2 38,2 Z" fill={`url(#${gradientId})`}/>
    </g>
  );

  const Text = () => (
     <text x="52" y="28" fontFamily="sans-serif" fontSize="24" fontWeight="600" fill="#2E3A59">
        subsora
      </text>
  );

  return (
    <svg 
      width={width || (iconOnly ? 42 : 172)} 
      height={height} 
      viewBox={iconOnly ? "0 0 42 42" : "0 0 172 42"} 
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        {/* 5. Указываем уникальные ID в определениях */}
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#1DE9B6' }} />
          <stop offset="100%" style={{ stopColor: '#7C4DFF' }} />
        </linearGradient>
        <filter id={shadowId} x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
          <feOffset dx="2" dy="3" result="offsetblur"/>
          <feComponentTransfer><feFuncA type="linear" slope="0.2"/></feComponentTransfer>
          <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      
      <Icon />
      {!iconOnly && <Text />}
    </svg>
  );
};