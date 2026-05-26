const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function apiUrl(path: string): string {
  return `${API_URL}${path}`;
}

export type ClientRecord = {
  id: number;
  client_type: string;
  ru_name: string | null;
  en_name: string | null;
  full_name_ru?: string | null;
  full_name_en?: string | null;
  inn: string | null;
  phone: string | null;
  email: string | null;
  telegram_id: string | null;
  telegram_username: string | null;
  citizenship: string | null;
  tax_residency_country: string | null;
  birth_date: string | null;
  birth_place: string | null;
  passport_type: string | null;
  passport_series_number: string | null;
  passport_issue_date: string | null;
  passport_issued_by: string | null;
  passport_department_code: string | null;
  passport_expires_at: string | null;
  registration_address: string | null;
  residential_address: string | null;
  bank_name: string | null;
  bank_account: string | null;
  bank_corr_account: string | null;
  bank_bik: string | null;
  bank_inn: string | null;
  bank_kpp: string | null;
  created_at?: string;
  updated_at?: string;
};

export type DocumentRequestRecord = {
  id: number;
  status: string;
  request_source: string;
  deal_id: number | null;
  client_id: number | null;
  client_name: string | null;
  client_inn: string | null;
  manager_id: number | null;
  manager_name: string | null;
  client_type: string | null;
  document_package_type: string | null;
  deal_type: string | null;
  payment_number: string | null;
  payment_date: string | null;
  contract_number: string | null;
  contract_date: string | null;
  offer_version: string | null;
  offer_date: string | null;
  total_amount: string | number | null;
  full_payment_amount: string | number | null;
  currency: string;
  agent_fee_percent: string | number | null;
  payment_amount: string | number | null;
  supplier_payment_equal: string | number | null;
  agent_fee_amount: string | number | null;
  crypto_asset: string | null;
  wallet_address: string | null;
  counterparty_name: string | null;
  counterparty_address: string | null;
  counterparty_tax_number: string | null;
  counterparty_registration_number: string | null;
  counterparty_bank_name: string | null;
  counterparty_bank_account: string | null;
  counterparty_bank_swift: string | null;
  counterparty_corr_bank: string | null;
  counterparty_corr_bank_bik: string | null;
  counterparty_corr_account: string | null;
  counterparty_corr_account_extra: string | null;
  payment_basis_type: string | null;
  payment_basis_number: string | null;
  payment_basis_date: string | null;
  payment_basis_description: string | null;
  client_comment: string | null;
  manager_comment: string | null;
  admin_comment: string | null;
  payload_json: Record<string, unknown> | null;
  generated_documents_json: Record<string, { title: string; file_name: string; download_url: string }> | null;
  requested_by_user_id: number | null;
  requested_by_role: string | null;
  request_type: string | null;
  comment: string | null;
  correction_comment: string | null;
  reviewed_by_user_id: number | null;
  issued_by_user_id: number | null;
  selected_template_id: number | null;
  generated_document_id: number | null;
  created_at: string;
  updated_at: string;
};

export type DealRecord = {
  id: number;
  deal_number: string;
  client_id: number;
  client_name: string | null;
  client_inn: string | null;
  client_phone: string | null;
  client_email: string | null;
  document_request_id: number | null;
  manager_id: number | null;
  manager_name: string | null;
  referral_id: number | null;
  referral_name: string | null;
  deal_direction: string;
  client_type: string;
  asset: string | null;
  status: string;
  contract_number: string | null;
  contract_date: string | null;
  payment_number: string | null;
  payment_date: string | null;
  full_payment_amount: string | number | null;
  amount_rub: string | number | null;
  supplier_payment_equal: string | number | null;
  agent_fee_amount: string | number | null;
  agent_fee_percent: string | number | null;
  currency: string;
  wallet_address: string | null;
  generated_documents_json: Record<string, { title: string; file_name: string; download_url: string }> | null;
  documents_status: string | null;
  client_rate: string | number | null;
  client_asset_amount: string | number | null;
  required_action: string | null;
  payment_received_amount: string | number | null;
  payment_received_at: string | null;
  comment: string | null;
  created_at: string;
  updated_at: string;
};

export type LiquidityPurchaseLotRecord = {
  id: number;
  asset: string;
  purchase_amount_rub: string | number;
  purchase_rate: string | number;
  purchased_asset_volume: string | number;
  used_asset_volume: string | number;
  remaining_asset_volume: string | number;
  status: string;
  source: string | null;
  comment: string | null;
  created_at: string;
  updated_at: string;
};

export type LiquidityAllocationRecord = {
  id: number;
  lot_id: number;
  deal_id: number;
  asset: string;
  asset_volume: string | number;
  allocation_rate: string | number;
  cost_basis_rub: string | number;
  comment: string | null;
  created_at: string;
};

export type LiquidityAllocationResult = {
  deal: DealRecord;
  allocations: LiquidityAllocationRecord[];
};

export async function apiGet<T>(path: string, token?: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      cache: "no-store",
      credentials: "include",
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function apiPost<T>(path: string, payload?: unknown): Promise<T | null> {
  try {
    const hasPayload = payload !== undefined;
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      credentials: "include",
      headers: hasPayload ? { "Content-Type": "application/json" } : {},
      body: hasPayload ? JSON.stringify(payload) : undefined
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function apiPostWithError<T>(path: string, payload?: unknown): Promise<{ data: T | null; error: string | null; status: number | null }> {
  try {
    const hasPayload = payload !== undefined;
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      credentials: "include",
      headers: hasPayload ? { "Content-Type": "application/json" } : {},
      body: hasPayload ? JSON.stringify(payload) : undefined
    });
    if (!response.ok) {
      const errorPayload = await response.json().catch(() => null);
      return { data: null, error: errorPayload?.detail || "Request failed", status: response.status };
    }
    return { data: (await response.json()) as T, error: null, status: response.status };
  } catch {
    return { data: null, error: "Network error", status: null };
  }
}

export async function apiPatch<T>(path: string, payload: unknown): Promise<T | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function apiDelete(path: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      method: "DELETE",
      credentials: "include"
    });
    return response.ok;
  } catch {
    return false;
  }
}
