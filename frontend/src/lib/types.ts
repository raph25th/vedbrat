export type Role = "client" | "manager" | "admin" | "director";

export type Client = {
  id: number;
  full_name_ru: string;
  full_name_en?: string;
  inn?: string;
  phone?: string;
  email?: string;
  profile_status: string;
  responsible_manager_id?: number;
};

export type CfaDeal = {
  id: number;
  deal_number: string;
  client_id: number;
  status: string;
  required_action?: string;
  amount_rub: number;
  client_rate?: number;
  client_asset_amount?: number;
  wallet_address?: string;
  manager_id?: number;
  referral_fee_value?: number;
  actual_close_rate?: number;
  gross_profit_usdt?: number;
  net_profit_usdt?: number;
  comment?: string;
  created_at: string;
};

export type TelegramChat = {
  id: number;
  telegram_chat_id: string;
  title: string;
  chat_type: "client_group" | "agent_group";
};

export type Referral = {
  id: number;
  name: string;
  default_fee_type: string;
  default_fee_value: number;
  status: string;
};

export type User = {
  id: number;
  name: string;
  email: string;
  role: Role;
  is_allowed_to_connect_bot: boolean;
};
