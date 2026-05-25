export type AdminRole = "director" | "admin" | "manager" | "client";

export type AdminClient = {
  id: number;
  fullNameRu: string;
  fullNameEn: string;
  inn: string;
  phone: string;
  email: string;
  passport: string;
  passportIssueDate: string;
  passportIssuedBy: string;
  passportDepartmentCode: string;
  registrationAddress: string;
  personalDataStatus: string;
  bankDetailsStatus: string;
};

export type AdminBankAccount = {
  id: number;
  clientId: number;
  recipientName: string;
  bankName: string;
  accountNumber: string;
  corrAccount: string;
  bic: string;
  bankInn: string;
  bankKpp: string;
  paymentPurpose: string;
  status: string;
};

export const currentAdminUser = {
  id: 1,
  name: "Анна Соколова",
  role: "director" as AdminRole
};

export const adminManagers = [
  { id: 1, name: "Анна Соколова", role: "director" },
  { id: 2, name: "Михаил Орлов", role: "manager" },
  { id: 3, name: "Елена Морозова", role: "admin" }
];

export const adminClients: AdminClient[] = [];

export const adminBankAccounts: AdminBankAccount[] = [];

export type AdminReferral = {
  id: number;
  name: string;
  type: string;
  defaultFeeType: string;
  defaultFeeBase: string;
  defaultFeeValue: number;
  status: string;
  dealsCount: number;
  accruedRub: number;
  accruedUsdt: number;
};

export type AdminDocumentTemplate = {
  id: number;
  name: string;
  slug: string;
  description: string;
  templateType: string;
  documentType: string;
  direction: string;
  clientType: string;
  compositionType: string;
  executor: string;
  version: string;
  isActive: boolean;
  fileName: string;
  uploadedBy: string;
  updatedAt: string;
  variables: Array<{ key: string; description?: string; source?: string; required?: boolean; example?: string }>;
  missingFields: string[];
  requiredFields: string[];
};

export type AdminTelegramChat = {
  id: number;
  title: string;
  telegramChatId: string;
  chatType: string;
  defaultClient: string;
  agent: string;
  manager: string;
  clientsCount: number;
  dealsCount: number;
  status: string;
};

export type AdminDocument = {
  id: number;
  dealId: number;
  type: string;
  status: string;
  issuedFile: string;
  signedFile: string;
  uploadedBy: string;
  uploadedAt: string;
  checkedBy: string;
  checkedAt: string;
};

export type AdminDeal = {
  id: number;
  dealNumber: string;
  clientId: number;
  managerId: number;
  telegramChat: string;
  sourceType: string;
  status: string;
  requiredAction: string;
  amountRub: number;
  rateMode: string;
  clientRate: number | null;
  clientAssetAmount: number | null;
  walletAddress: string;
  clientPaymentStatus: string;
  paymentReceivedAt: string;
  referralId: number | null;
  referralName: string;
  referralFeeType: string;
  referralFeeBase: string;
  referralFeeValue: number;
  referralFeeRub: number;
  referralFeeUsdt: number;
  actualCloseRate: number | null;
  actualAssetAmount: number | null;
  grossProfitUsdt: number | null;
  grossProfitRub: number | null;
  netProfitUsdt: number | null;
  netProfitRub: number | null;
  documentsStatus: string;
  createdAt: string;
  updatedAt: string;
};

export type AdminHistoryItem = {
  id: number;
  dealId: number;
  title: string;
  detail: string;
  date: string;
};
export const adminReferrals: AdminReferral[] = [];

export const documentTemplateTypeLabels: Record<string, string> = {
  contract: "Договор",
  offer_join_statement: "Заявление о присоединении",
  principal_order: "Поручение",
  agent_report: "Акт",
  package: "Пакет документов",
  additional: "Дополнительный документ"
};

export const directionLabels: Record<string, string> = {
  cfa: "ЦФА",
  crypto: "Крипта",
  cars: "Авто/тачки",
  ved: "ВЭД",
  common: "Общее"
};

export const clientTypeLabels: Record<string, string> = {
  physical_person: "Физлицо",
  individual_entrepreneur: "ИП",
  legal_entity: "Юрлицо",
  any: "Любой"
};

export const compositionTypeLabels: Record<string, string> = {
  single_document: "Одиночный документ",
  package: "Пакет"
};

export const adminDocumentTemplateVariables = [
  { key: "contract.number", description: "Номер договора", source: "Contract.contract_number", required: true, example: "CFA-2026-001" },
  { key: "contract.date", description: "Дата договора", source: "Contract.contract_date", required: true, example: "24.05.2026" },
  { key: "executor.ru.name", description: "Наименование исполнителя", source: "Executor.name_ru", required: true, example: "ООО ВЕДБРАТ" },
  { key: "executor.ru.form", description: "Правовая форма исполнителя", source: "Executor.legal_form", required: true, example: "Общество с ограниченной ответственностью" },
  { key: "customer.ru.name", description: "ФИО клиента RU", source: "Client.full_name_ru", required: true, example: "Иванов Алексей Сергеевич" },
  { key: "customer.en.name", description: "ФИО клиента EN", source: "Client.full_name_en", required: false, example: "Alexey Ivanov" },
  { key: "customer.inn", description: "ИНН клиента", source: "Client.inn", required: true, example: "770000000000" },
  { key: "customer.email", description: "Email клиента", source: "Client.email", required: true, example: "client@example.com" },
  { key: "customer_account.payment_account", description: "Расчетный счет клиента", source: "ClientBankAccount.account_number", required: true, example: "40817810000000000001" },
  { key: "customer_account.bic", description: "БИК банка клиента", source: "ClientBankAccount.bic", required: true, example: "044525225" }
];

export const adminDocumentTemplates: AdminDocumentTemplate[] = [];

export const adminTelegramChats: AdminTelegramChat[] = [];

export const documentStatusLabels: Record<string, string> = {
  requested: "Запрошен",
  preparing: "Готовится",
  uploaded: "Загружен",
  issued_to_client: "Выдан клиенту",
  waiting_for_signature: "Ожидает подписи",
  signed_uploaded: "Подписанный файл загружен",
  checked: "Проверен",
  replacement_required: "Требует замены"
};

export const adminDocuments: AdminDocument[] = [];

export const adminDeals: AdminDeal[] = [];

export const adminHistory: AdminHistoryItem[] = [];

export function getAdminClient(clientId: number) {
  return adminClients.find((client) => client.id === clientId);
}

export function getAdminManager(managerId: number) {
  return adminManagers.find((manager) => manager.id === managerId);
}

export function canSeeFinance(role: AdminRole) {
  return role === "director" || role === "admin" || role === "manager";
}
