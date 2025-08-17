import type { Plan } from './plan';
import type { User } from './user';

export interface Subscription {
    id: number;
    user_id: number;
    plan_id: number;
    start_date: string;
    end_date: string;
    user: User;
    plan: Plan;
}