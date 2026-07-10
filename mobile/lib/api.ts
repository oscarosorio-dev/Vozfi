const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export type Transaction = {
  id: string;
  type: 'income' | 'expense';
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

export type CategorySummary = {
  category: string;
  type: 'income' | 'expense';
  total: number;
};

export type MonthlySummary = {
  month: string;
  income: number;
  expense: number;
  balance: number;
};

export type TransactionUpdate = Partial<{
  type: 'income' | 'expense';
  amount: number;
  category: string;
  description: string | null;
  occurred_at: string;
}>;

export type VoiceInputResponse = {
  transcript: string;
  reply: string;
  audio_base64: string | null;
  audio_content_type: string | null;
};

class ApiError extends Error {}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(body.detail ?? `Error ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getBalance(): Promise<Balance> {
  const response = await fetch(`${API_URL}/summary/balance`);
  return handleResponse<Balance>(response);
}

export async function getCategorySummary(): Promise<CategorySummary[]> {
  const response = await fetch(`${API_URL}/summary/by-category`);
  return handleResponse<CategorySummary[]>(response);
}

export async function getMonthlySummary(): Promise<MonthlySummary[]> {
  const response = await fetch(`${API_URL}/summary/by-month`);
  return handleResponse<MonthlySummary[]>(response);
}

export async function listTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_URL}/transactions`);
  return handleResponse<Transaction[]>(response);
}

export async function getTransaction(id: string): Promise<Transaction> {
  const response = await fetch(`${API_URL}/transactions/${id}`);
  return handleResponse<Transaction>(response);
}

export async function updateTransaction(id: string, data: TransactionUpdate): Promise<Transaction> {
  const response = await fetch(`${API_URL}/transactions/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Transaction>(response);
}

export async function deleteTransaction(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/transactions/${id}`, { method: 'DELETE' });
  if (!response.ok && response.status !== 204) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new ApiError(body.detail ?? `Error ${response.status}`);
  }
}

/**
 * Envía un audio grabado al pipeline de voz (STT -> agente -> TTS).
 * `uri` es un archivo local (file://...) producido por expo-audio.
 */
export async function sendVoiceInput(uri: string, mimeType: string): Promise<VoiceInputResponse> {
  const extension = mimeType.split('/')[1]?.split(';')[0] ?? 'm4a';
  const formData = new FormData();
  // React Native FormData espera este shape { uri, name, type }, no un Blob como en web.
  formData.append('file', {
    uri,
    name: `audio.${extension}`,
    type: mimeType,
  } as unknown as Blob);

  const response = await fetch(`${API_URL}/voice/voice-input`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse<VoiceInputResponse>(response);
}