export const clientStatusLabels: Record<string, string> = {
  empty: "Пустой",
  personal_data_started: "Заполняет",
  personal_data_submitted: "На проверке",
  personal_data_approved: "Данные одобрены",
  bank_details_submitted: "Реквизиты на проверке",
  bank_details_approved: "Реквизиты одобрены",
  contract_ready: "Договор готов",
  contract_signed: "Договор подписан",
  active: "Активен"
};

export const dealStatusLabels: Record<string, string> = {
  new_request: "Новая заявка",
  client_data_required: "Нужны данные",
  client_data_submitted: "Данные на проверке",
  client_data_approved: "Данные одобрены",
  bank_details_required: "Нужны реквизиты",
  bank_details_submitted: "Реквизиты на проверке",
  bank_details_approved: "Реквизиты одобрены",
  documents_requested: "Запрошены документы",
  documents_generated: "Документы готовы",
  waiting_for_signature: "Ожидает подпись",
  documents_signed: "Документы подписаны",
  waiting_for_client_payment: "Ожидает оплату",
  client_payment_received: "Оплата получена",
  rate_required: "Нужен курс",
  rate_fixed: "Курс зафиксирован",
  wallet_required: "Нужен кошелек",
  wallet_submitted: "Кошелек указан",
  ready_for_execution: "Готово к исполнению",
  executed: "Исполнено",
  report_generated: "Отчет готов",
  waiting_report_signature: "Ожидает подпись отчета",
  report_signed: "Отчет подписан",
  completed: "Завершено",
  cancelled: "Отменено",
  needs_correction: "Нужна корректировка"
};

export function statusTone(status: string) {
  if (["completed", "active", "executed", "client_data_approved", "bank_details_approved"].includes(status)) {
    return "success";
  }
  if (["cancelled", "needs_correction"].includes(status)) {
    return "danger";
  }
  if (status.includes("waiting") || status.includes("required") || status.includes("submitted")) {
    return "warning";
  }
  return "neutral";
}
