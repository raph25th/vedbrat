import { Download, FilePlus2, Upload } from "lucide-react";
import { MiniStatusBadge } from "@/components/mini-status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { miniDeals, miniDocuments } from "@/lib/mock-data";

export default function DocumentsPage() {
  const activeDeal = miniDeals[0];
  const documents = miniDocuments.filter((document) => document.dealId === activeDeal.id);

  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-1 pt-1">
        <h1 className="text-2xl font-semibold text-slate-50">Документы</h1>
        <p className="text-sm text-slate-400">Комплект сделки и подписанные файлы.</p>
      </header>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Документы по {activeDeal.dealNumber}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {documents.map((document) => (
            <div key={document.id} className="space-y-3 rounded-xl border border-slate-700/50 bg-slate-950/25 p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-slate-100">{document.title}</div>
                  <div className="mt-1 text-xs text-slate-500">{document.type}</div>
                </div>
                <MiniStatusBadge status={document.status} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Button variant="secondary" size="sm" disabled={!document.canDownload}>
                  <Download className="h-4 w-4" />
                  Скачать
                </Button>
                <Button size="sm" disabled={!document.canUploadSigned}>
                  <Upload className="h-4 w-4" />
                  Подписанный файл
                </Button>
              </div>
            </div>
          ))}
          <div className="grid gap-2">
            <Button variant="outline" className="w-full justify-start">
              <FilePlus2 className="h-4 w-4" />
              Запросить документы
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Загрузка файла</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Тип документа</Label>
            <Input placeholder="Договор / Отчет" />
          </div>
          <div className="space-y-2">
            <Label>Файл</Label>
            <Input type="file" />
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
