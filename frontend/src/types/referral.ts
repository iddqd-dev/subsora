import type { User } from './user';

export interface Referral {
    id: number;
    referrer_id: number;
    referred_id: number;
    created_at: string;
    // Схемы Read возвращают вложенные объекты
    referrer: User;
    referred: User;
}