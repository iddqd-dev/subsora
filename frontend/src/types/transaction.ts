import type { Subscription } from './subscription';
import type { User } from './user';
import type { Plan } from './plan'; // Возможно, понадобится

export interface Transaction {
    id: number;
    user_id: number;
    amount: number;
    currency: string;
    status: 'completed' | 'pending' | 'failed';
    subscription_id: number | null;
    created_at: string;
    user: User;
    // Наша "жадная" загрузка в subscription включает и plan
    subscription: (Subscription & { plan: Plan }) | null;
    plan_id: number | null; // Мы добавили это поле
}