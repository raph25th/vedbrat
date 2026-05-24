import type { CfaDeal, Client, Referral, TelegramChat, User } from "./types";

export const clients: Client[] = [
  {
    id: 1,
    full_name_ru: "Иванов Алексей Сергеевич",
    full_name_en: "Alexey Ivanov",
    inn: "770000000000",
    phone: "+7 999 111-22-33",
    email: "client@example.com",
    profile_status: "bank_details_approved",
    responsible_manager_id: 2
  },
  {
    id: 2,
    full_name_ru: "Петрова Мария Андреевна",
    full_name_en: "Maria Petrova",
    phone: "+7 999 444-55-66",
    email: "maria@example.com",
    profile_status: "personal_data_submitted",
    responsible_manager_id: 2
  }
];

export const deals: CfaDeal[] = [
  {
    id: 1,
    deal_number: "CFA-2026-001",
    client_id: 1,
    status: "waiting_for_client_payment",
    required_action: "Ожидается поступление рублей",
    amount_rub: 12500000,
    client_rate: 92.4,
    client_asset_amount: 135281.39,
    wallet_address: "TQ9x...zP2a",
    manager_id: 2,
    referral_fee_value: 0.4,
    actual_close_rate: 91.8,
    gross_profit_usdt: 884.19,
    net_profit_usdt: 342.91,
    comment: "Проверить назначение платежа перед исполнением.",
    created_at: "2026-05-24T09:00:00Z"
  },
  {
    id: 2,
    deal_number: "CFA-2026-002",
    client_id: 2,
    status: "client_data_submitted",
    required_action: "Проверить паспортные данные",
    amount_rub: 4300000,
    client_rate: 92.1,
    client_asset_amount: 46688.38,
    manager_id: 2,
    created_at: "2026-05-23T15:20:00Z"
  }
];

export const telegramChats: TelegramChat[] = [
  { id: 1, telegram_chat_id: "-100111222333", title: "Ivanov CFA", chat_type: "client_group" },
  { id: 2, telegram_chat_id: "-100444555666", title: "Agent North Desk", chat_type: "agent_group" }
];

export const referrals: Referral[] = [
  { id: 1, name: "Referral Desk A", default_fee_type: "percent", default_fee_value: 0.3, status: "active" },
  { id: 2, name: "Fixed Partner", default_fee_type: "fixed_usdt", default_fee_value: 250, status: "active" }
];

export const users: User[] = [
  { id: 1, name: "Анна Админ", email: "admin@example.com", role: "admin", is_allowed_to_connect_bot: true },
  { id: 2, name: "Михаил Менеджер", email: "manager@example.com", role: "manager", is_allowed_to_connect_bot: true },
  { id: 3, name: "Алексей Иванов", email: "client@example.com", role: "client", is_allowed_to_connect_bot: false }
];
