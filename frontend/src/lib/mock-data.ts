export type MiniClientProfile = {
  id: number;
  fullNameRu: string;
  fullNameEn: string;
  inn: string;
  citizenship: string;
  taxResidency: string;
  birthDate: string;
  birthPlace: string;
  phone: string;
  email: string;
  passportNumber: string;
  passportIssueDate: string;
  passportIssuedBy: string;
  passportDepartmentCode: string;
  registrationAddress: string;
  profileStatus: string;
  bankDetailsStatus: string;
};

export type MiniBankAccount = {
  id: number;
  recipientName: string;
  bankName: string;
  accountNumber: string;
  corrAccount: string;
  bic: string;
  bankInn: string;
  bankKpp: string;
  paymentPurpose: string;
  isDefault: boolean;
  status: string;
};

export type MiniDeal = {
  id: number;
  dealNumber: string;
  status: string;
  amountRub: number;
  clientRate: number | null;
  clientAssetAmount: number | null;
  walletAddress: string | null;
  documentsStatus: string;
  requiredAction: string | null;
  statusHistory: Array<{ id: number; label: string; date: string }>;
};

export type MiniDocument = {
  id: number;
  dealId: number;
  title: string;
  type: string;
  status: string;
  canDownload: boolean;
  canUploadSigned: boolean;
};

export const miniClient: MiniClientProfile = {
  id: 0,
  fullNameRu: "",
  fullNameEn: "",
  inn: "",
  citizenship: "",
  taxResidency: "",
  birthDate: "",
  birthPlace: "",
  phone: "",
  email: "",
  passportNumber: "",
  passportIssueDate: "",
  passportIssuedBy: "",
  passportDepartmentCode: "",
  registrationAddress: "",
  profileStatus: "empty",
  bankDetailsStatus: "empty"
};

export const miniBankAccounts: MiniBankAccount[] = [];

export const miniDeals: MiniDeal[] = [
  {
    id: 1,
    dealNumber: "CFA-2026-001",
    status: "waiting_for_client_payment",
    amountRub: 12500000,
    clientRate: 92.4,
    clientAssetAmount: 135281.39,
    walletAddress: "TQ9x...zP2a",
    documentsStatus: "waiting_for_signature",
    requiredAction: "ожидаем поступление оплаты",
    statusHistory: [
      { id: 1, label: "Заявка создана", date: "24.05.2026" },
      { id: 2, label: "Документы выданы клиенту", date: "24.05.2026" },
      { id: 3, label: "Ожидается оплата", date: "24.05.2026" }
    ]
  },
  {
    id: 2,
    dealNumber: "CFA-2026-002",
    status: "client_data_submitted",
    amountRub: 4300000,
    clientRate: 92.1,
    clientAssetAmount: 46688.38,
    walletAddress: null,
    documentsStatus: "requested",
    requiredAction: "Данные находятся на проверке",
    statusHistory: [
      { id: 1, label: "Заявка создана", date: "23.05.2026" },
      { id: 2, label: "Данные отправлены на проверку", date: "23.05.2026" }
    ]
  }
];

export const miniDocuments: MiniDocument[] = [
  {
    id: 1,
    dealId: 1,
    title: "Договор поручения",
    type: "contract",
    status: "waiting_for_signature",
    canDownload: true,
    canUploadSigned: true
  },
  {
    id: 2,
    dealId: 1,
    title: "Отчет CFA",
    type: "report",
    status: "preparing",
    canDownload: false,
    canUploadSigned: false
  },
  {
    id: 3,
    dealId: 2,
    title: "Комплект документов",
    type: "deal_package",
    status: "requested",
    canDownload: false,
    canUploadSigned: false
  }
];
