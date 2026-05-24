export type AdminRole = "director" | "admin" | "manager" | "client";

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

export const adminClients = [
  {
    id: 1,
    fullNameRu: "Иванов Алексей Сергеевич",
    fullNameEn: "Alexey Ivanov",
    inn: "770000000000",
    phone: "+7 999 111-22-33",
    email: "client@example.com",
    passport: "4512 345678",
    passportIssueDate: "20.05.2019",
    passportIssuedBy: "ГУ МВД России по г. Москве",
    passportDepartmentCode: "770-001",
    registrationAddress: "г. Москва, ул. Примерная, д. 10, кв. 25",
    personalDataStatus: "personal_data_approved",
    bankDetailsStatus: "bank_details_approved"
  },
  {
    id: 2,
    fullNameRu: "Петрова Мария Андреевна",
    fullNameEn: "Maria Petrova",
    inn: "780000000000",
    phone: "+7 999 444-55-66",
    email: "maria@example.com",
    passport: "4018 987654",
    passportIssueDate: "11.02.2021",
    passportIssuedBy: "ГУ МВД России по Санкт-Петербургу",
    passportDepartmentCode: "780-002",
    registrationAddress: "г. Санкт-Петербург, Невский пр., д. 15",
    personalDataStatus: "personal_data_submitted",
    bankDetailsStatus: "bank_details_submitted"
  },
  {
    id: 3,
    fullNameRu: "Смирнов Дмитрий Павлович",
    fullNameEn: "Dmitry Smirnov",
    inn: "500000000000",
    phone: "+7 999 777-88-99",
    email: "dmitry@example.com",
    passport: "4615 111222",
    passportIssueDate: "03.08.2020",
    passportIssuedBy: "ГУ МВД России по Московской области",
    passportDepartmentCode: "500-003",
    registrationAddress: "Московская область, г. Одинцово, ул. Центральная, д. 4",
    personalDataStatus: "active",
    bankDetailsStatus: "bank_details_approved"
  }
];

export const adminBankAccounts = [
  {
    id: 1,
    clientId: 1,
    recipientName: "Иванов Алексей Сергеевич",
    bankName: "АО Тест Банк",
    accountNumber: "40817810000000000001",
    corrAccount: "30101810000000000225",
    bic: "044525225",
    bankInn: "7700000001",
    bankKpp: "770001001",
    paymentPurpose: "Оплата по договору поручения",
    status: "bank_details_approved"
  },
  {
    id: 2,
    clientId: 2,
    recipientName: "Петрова Мария Андреевна",
    bankName: "ПАО Северный Банк",
    accountNumber: "40817810000000000002",
    corrAccount: "30101810100000000888",
    bic: "044030888",
    bankInn: "7800000002",
    bankKpp: "780001001",
    paymentPurpose: "Перечисление по сделке ЦФА",
    status: "bank_details_submitted"
  }
];

export const adminReferrals = [
  {
    id: 1,
    name: "Referral Desk A",
    type: "partner",
    defaultFeeType: "percent",
    defaultFeeBase: "client_amount_rub",
    defaultFeeValue: 0.3,
    status: "active",
    dealsCount: 8,
    accruedRub: 850000,
    accruedUsdt: 9300
  },
  {
    id: 2,
    name: "Fixed Partner",
    type: "agent",
    defaultFeeType: "fixed_usdt",
    defaultFeeBase: "client_asset_amount",
    defaultFeeValue: 250,
    status: "active",
    dealsCount: 3,
    accruedRub: 180000,
    accruedUsdt: 1950
  }
];

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

export const adminDocumentTemplates = [
  {
    id: 1,
    name: "Заявление о присоединении к оферте",
    slug: "offer-join-statement-physical-cfa",
    description: "Заявление клиента-физлица о присоединении к оферте.",
    templateType: "offer_join_statement",
    documentType: "offer_join_statement",
    direction: "cfa",
    clientType: "physical_person",
    compositionType: "single_document",
    executor: "RSI",
    version: "1.0",
    isActive: true,
    fileName: "offer-join-statement-physical-cfa-v1.docx",
    uploadedBy: "Елена Морозова",
    updatedAt: "24.05.2026 13:20",
    variables: adminDocumentTemplateVariables.slice(0, 8),
    missingFields: ["executor.ru.executive_body_type", "executor.ru.executive_body_name"],
    requiredFields: ["contract.number", "contract.date", "customer.ru.name", "customer.inn"]
  },
  {
    id: 2,
    name: "Агентский договор RSI под крипту для физика",
    slug: "rsi-agent-contract-crypto-physical",
    description: "Пакетный агентский договор RSI под крипто-направление для физлица, включает приложения.",
    templateType: "contract",
    documentType: "contract",
    direction: "crypto",
    clientType: "physical_person",
    compositionType: "package",
    executor: "RSI",
    version: "1.0",
    isActive: true,
    fileName: "rsi-agent-contract-crypto-physical-v1.docx",
    uploadedBy: "Михаил Орлов",
    updatedAt: "23.05.2026 17:10",
    variables: adminDocumentTemplateVariables,
    missingFields: ["contractCustom.agent_country_ru", "contractCustom.agent_country_en"],
    requiredFields: ["contract.number", "customer.ru.name", "customer.inn", "customer_account.payment_account"]
  },
  {
    id: 3,
    name: "Агентский договор RSI под крипту для ИП",
    slug: "rsi-agent-contract-crypto-ip",
    description: "Пакетный агентский договор RSI под крипто-направление для индивидуального предпринимателя.",
    templateType: "contract",
    documentType: "contract",
    direction: "crypto",
    clientType: "individual_entrepreneur",
    compositionType: "package",
    executor: "RSI",
    version: "1.0",
    isActive: true,
    fileName: "rsi-agent-contract-crypto-ip-v1.docx",
    uploadedBy: "Анна Соколова",
    updatedAt: "20.05.2026 12:00",
    variables: adminDocumentTemplateVariables,
    missingFields: ["customer.ogrnip", "customer.registration_address"],
    requiredFields: ["contract.number", "customer.ru.name", "customer.inn"]
  },
  {
    id: 4,
    name: "Агентский договор RSI под крипту для юрлиц",
    slug: "rsi-agent-contract-crypto-legal",
    description: "Пакетный агентский договор RSI под крипто-направление для юридических лиц.",
    templateType: "contract",
    documentType: "contract",
    direction: "crypto",
    clientType: "legal_entity",
    compositionType: "package",
    executor: "RSI",
    version: "1.0",
    isActive: true,
    fileName: "rsi-agent-contract-crypto-legal-v1.docx",
    uploadedBy: "Елена Морозова",
    updatedAt: "19.05.2026 16:40",
    variables: adminDocumentTemplateVariables,
    missingFields: ["customer.ogrn", "customer.executive_body_name", "customer.authority_doc"],
    requiredFields: ["contract.number", "customer.ru.name", "customer.inn", "customer.email"]
  },
  {
    id: 5,
    name: "Агентский договор RSI под авто/тачки",
    slug: "rsi-agent-contract-cars-any",
    description: "Пакетный агентский договор RSI для автомобильного направления.",
    templateType: "contract",
    documentType: "contract",
    direction: "cars",
    clientType: "any",
    compositionType: "package",
    executor: "RSI",
    version: "1.0",
    isActive: true,
    fileName: "rsi-agent-contract-cars-any-v1.docx",
    uploadedBy: "Михаил Орлов",
    updatedAt: "18.05.2026 10:20",
    variables: adminDocumentTemplateVariables.slice(0, 9),
    missingFields: ["car.vin", "car.brand", "car.model"],
    requiredFields: ["contract.number", "customer.ru.name", "customer.inn"]
  }
];

export const adminTelegramChats = [
  {
    id: 1,
    title: "Ivanov CFA",
    telegramChatId: "-100111222333",
    chatType: "client_group",
    defaultClient: "Иванов Алексей Сергеевич",
    agent: "—",
    manager: "Михаил Орлов",
    clientsCount: 1,
    dealsCount: 2,
    status: "active"
  },
  {
    id: 2,
    title: "Agent North Desk",
    telegramChatId: "-100444555666",
    chatType: "agent_group",
    defaultClient: "—",
    agent: "Referral Desk A",
    manager: "Анна Соколова",
    clientsCount: 7,
    dealsCount: 11,
    status: "active"
  },
  {
    id: 3,
    title: "Petrova CFA",
    telegramChatId: "-100777888999",
    chatType: "client_group",
    defaultClient: "Петрова Мария Андреевна",
    agent: "—",
    manager: "Михаил Орлов",
    clientsCount: 1,
    dealsCount: 1,
    status: "pending"
  }
];

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

export const adminDocuments = [
  {
    id: 1,
    dealId: 1,
    type: "Агентский договор",
    status: "checked",
    issuedFile: "agency-contract-cfa-2026-001.pdf",
    signedFile: "agency-contract-cfa-2026-001-signed.pdf",
    uploadedBy: "Елена Морозова",
    uploadedAt: "24.05.2026 11:10",
    checkedBy: "Анна Соколова",
    checkedAt: "24.05.2026 12:40"
  },
  {
    id: 2,
    dealId: 1,
    type: "Поручение принципала",
    status: "waiting_for_signature",
    issuedFile: "principal-order-cfa-2026-001.pdf",
    signedFile: "—",
    uploadedBy: "Елена Морозова",
    uploadedAt: "24.05.2026 11:15",
    checkedBy: "—",
    checkedAt: "—"
  },
  {
    id: 3,
    dealId: 1,
    type: "Инвойс / платежный документ",
    status: "issued_to_client",
    issuedFile: "invoice-cfa-2026-001.pdf",
    signedFile: "—",
    uploadedBy: "Михаил Орлов",
    uploadedAt: "24.05.2026 11:30",
    checkedBy: "—",
    checkedAt: "—"
  },
  {
    id: 4,
    dealId: 1,
    type: "Акт-отчет",
    status: "preparing",
    issuedFile: "—",
    signedFile: "—",
    uploadedBy: "—",
    uploadedAt: "—",
    checkedBy: "—",
    checkedAt: "—"
  },
  {
    id: 5,
    dealId: 1,
    type: "Дополнительный документ",
    status: "requested",
    issuedFile: "—",
    signedFile: "—",
    uploadedBy: "—",
    uploadedAt: "—",
    checkedBy: "—",
    checkedAt: "—"
  }
];

export const adminDeals = [
  {
    id: 1,
    dealNumber: "CFA-2026-001",
    clientId: 1,
    managerId: 2,
    telegramChat: "Ivanov CFA",
    sourceType: "client_group",
    status: "waiting_for_client_payment",
    requiredAction: "Проверить поступление оплаты",
    amountRub: 12500000,
    rateMode: "manual_fixed",
    clientRate: 92.4,
    clientAssetAmount: 135281.39,
    walletAddress: "TQ9x...zP2a",
    clientPaymentStatus: "Ожидаем оплату",
    paymentReceivedAt: "—",
    referralId: 1,
    referralName: "Referral Desk A",
    referralFeeType: "percent",
    referralFeeBase: "client_amount_rub",
    referralFeeValue: 0.3,
    referralFeeRub: 37500,
    referralFeeUsdt: 408.5,
    actualCloseRate: 91.8,
    actualAssetAmount: 136165.58,
    grossProfitUsdt: 884.19,
    grossProfitRub: 81168,
    netProfitUsdt: 475.69,
    netProfitRub: 43668,
    documentsStatus: "waiting_for_signature",
    createdAt: "24.05.2026",
    updatedAt: "24.05.2026 12:40"
  },
  {
    id: 2,
    dealNumber: "CFA-2026-002",
    clientId: 2,
    managerId: 2,
    telegramChat: "Petrova CFA",
    sourceType: "client_group",
    status: "client_data_submitted",
    requiredAction: "Проверить данные клиента",
    amountRub: 4300000,
    rateMode: "cb_plus_percent",
    clientRate: 92.1,
    clientAssetAmount: 46688.38,
    walletAddress: "—",
    clientPaymentStatus: "Не поступила",
    paymentReceivedAt: "—",
    referralId: null,
    referralName: "—",
    referralFeeType: "—",
    referralFeeBase: "—",
    referralFeeValue: 0,
    referralFeeRub: 0,
    referralFeeUsdt: 0,
    actualCloseRate: null,
    actualAssetAmount: null,
    grossProfitUsdt: null,
    grossProfitRub: null,
    netProfitUsdt: null,
    netProfitRub: null,
    documentsStatus: "requested",
    createdAt: "23.05.2026",
    updatedAt: "24.05.2026 10:20"
  },
  {
    id: 3,
    dealNumber: "CFA-2026-003",
    clientId: 3,
    managerId: 1,
    telegramChat: "Manual",
    sourceType: "manual_admin",
    status: "rate_required",
    requiredAction: "Зафиксировать курс",
    amountRub: 8900000,
    rateMode: "after_payment_manual",
    clientRate: null,
    clientAssetAmount: null,
    walletAddress: "TAbc...91d",
    clientPaymentStatus: "Деньги поступили",
    paymentReceivedAt: "24.05.2026 09:15",
    referralId: 2,
    referralName: "Fixed Partner",
    referralFeeType: "fixed_usdt",
    referralFeeBase: "client_asset_amount",
    referralFeeValue: 250,
    referralFeeRub: 22950,
    referralFeeUsdt: 250,
    actualCloseRate: null,
    actualAssetAmount: null,
    grossProfitUsdt: null,
    grossProfitRub: null,
    netProfitUsdt: null,
    netProfitRub: null,
    documentsStatus: "checked",
    createdAt: "22.05.2026",
    updatedAt: "24.05.2026 09:30"
  },
  {
    id: 4,
    dealNumber: "CFA-2026-004",
    clientId: 1,
    managerId: 3,
    telegramChat: "Agent North Desk",
    sourceType: "agent_group",
    status: "completed",
    requiredAction: "—",
    amountRub: 2500000,
    rateMode: "manual_fixed",
    clientRate: 91.7,
    clientAssetAmount: 27262.81,
    walletAddress: "TDone...49q",
    clientPaymentStatus: "Оплата получена",
    paymentReceivedAt: "12.05.2026 14:00",
    referralId: 1,
    referralName: "Referral Desk A",
    referralFeeType: "percent",
    referralFeeBase: "profit",
    referralFeeValue: 10,
    referralFeeRub: 9000,
    referralFeeUsdt: 98.1,
    actualCloseRate: 91.1,
    actualAssetAmount: 27442.37,
    grossProfitUsdt: 179.56,
    grossProfitRub: 16360,
    netProfitUsdt: 81.46,
    netProfitRub: 7360,
    documentsStatus: "checked",
    createdAt: "10.05.2026",
    updatedAt: "15.05.2026 18:00"
  }
];

export const adminHistory = [
  { id: 1, dealId: 1, title: "Сделка создана", detail: "Источник client_group", date: "24.05.2026 09:00" },
  { id: 2, dealId: 1, title: "Данные клиента подтверждены", detail: "Проверил Михаил Орлов", date: "24.05.2026 10:10" },
  { id: 3, dealId: 1, title: "Документы загружены", detail: "Поручение принципала выдано клиенту", date: "24.05.2026 11:15" },
  { id: 4, dealId: 1, title: "Курс зафиксирован", detail: "Курс клиента 92.4", date: "24.05.2026 11:50" },
  { id: 5, dealId: 1, title: "Статус изменен", detail: "Ожидаем оплату", date: "24.05.2026 12:40" }
];

export function getAdminClient(clientId: number) {
  return adminClients.find((client) => client.id === clientId);
}

export function getAdminManager(managerId: number) {
  return adminManagers.find((manager) => manager.id === managerId);
}

export function canSeeFinance(role: AdminRole) {
  return role === "director" || role === "admin" || role === "manager";
}
