import {
    Star as StarIcon,
    Whatshot as WhatshotIcon,
    EmojiEvents as TrophyIcon,
    WorkspacePremium as PremiumIcon,
  } from '@mui/icons-material';
  import type { ElementType } from 'react';
  import type { Palette } from '@mui/material';
  import type { ReferralTierAPI } from '../../hooks/useReferralTiers';
  
  // Расширенный тип, который используется в компонентах
  export interface DiscountLevel {
    referrals: number;
    discount: number;
    title: string;
    Icon: ElementType;
    color: keyof Omit<Palette, 'modes' | 'common' | 'grey' | 'text' | 'divider' | 'action' | 'background'> | 'grey';
  }
  
  // Карта для хранения визуальных атрибутов. Ключ - количество рефералов.
  const PRESENTATION_MAP: Record<number, Omit<DiscountLevel, 'referrals' | 'discount'>> = {
    0:    { title: 'Новичок',  Icon: StarIcon,         color: 'grey' },
    5:    { title: 'Активный', Icon: WhatshotIcon,     color: 'warning' },
    15:   { title: 'Эксперт',  Icon: TrophyIcon,       color: 'primary' },
    30:   { title: 'Легенда',  Icon: PremiumIcon,      color: 'secondary' },
  };
  
  // Функция, которая обогащает данные с бэкенда
  export const enrichTiers = (apiTiers: ReferralTierAPI[]): DiscountLevel[] => {
    // Добавляем базовый уровень "0 рефералов"
    const allTiersData = [{ referrals: 0, discount: 0 }, ...apiTiers];
  
    // Сортируем на случай, если бэкенд вернет вразнобой
    allTiersData.sort((a, b) => a.referrals - b.referrals);
  
    return allTiersData.map(tier => {
      // Находим визуальные атрибуты по количеству рефералов
      const presentation = PRESENTATION_MAP[tier.referrals] || PRESENTATION_MAP[0]; // Fallback на новичка
      
      return {
        ...tier,
        ...presentation
      };
    });
  };
  