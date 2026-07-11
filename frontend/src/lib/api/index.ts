const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Transaction = {
  id: string;
  type: "income" | "expense";
  amount: number;
  category: string;
  description: string | null;
  occurred_at: string;
  created_at: string;
};

export type Balance = {
  income: number;
  expense: number;
  balance: number;
};

export type MonthlySummary = {
  month: string;
  income: number;
  expense: number;
  balance: number;
};

export type VoiceInputResponse = {
  transcript: string;
  reply: string;
  audio_base64: string | null;
  audio_content_type: string | null;
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? `Error ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getBalance(): Promise<Balance> {
  const response = await fetch(`${API_URL}/summary/balance`, { cache: "no-store" });
  return handleResponse<Balance>(response);
}

export async function listTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_URL}/transactions`, { cache: "no-store" });
  return handleResponse<Transaction[]>(response);
}

export async function getMonthlySummary(): Promise<MonthlySummary[]> {
  const response = await fetch(`${API_URL}/summary/by-month`, { cache: "no-store" });
  return handleResponse<MonthlySummary[]>(response);
}

export async function sendVoiceInput(audio: Blob): Promise<VoiceInputResponse> {
  const formData = new FormData();
  formData.append("file", audio, "audio.webm");

  const response = await fetch(`${API_URL}/voice/voice-input`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<VoiceInputResponse>(response);
}