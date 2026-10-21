export type SSEEvent = { event: string; data: string };

export class Utf8Chunker {
  push(bytes: Uint8Array): string {
    throw new Error("not implemented");
  }
  end(): string {
    throw new Error("not implemented");
  }
}

export class SSEParser {
  push(text: string): SSEEvent[] {
    throw new Error("not implemented");
  }
  end(): SSEEvent[] {
    throw new Error("not implemented");
  }
}

export function accumulateText(events: SSEEvent[]): string {
  throw new Error("not implemented");
}

// Part B · a streaming client for the BFF's delta/done/error events

export const SESSION_EXPIRED = "Your session has expired. Sign in again.";
export const CONNECTION_LOST = "Connection lost. Check your network and retry.";
export const UNAVAILABLE = "The assistant is unavailable.";

export class AuthExpiredError extends Error {}

type StreamResponse = { ok: boolean; status: number; body: AsyncIterable<Uint8Array> | null };
export type StreamFetch = (url: string, init: {
  method: string; headers: Record<string, string>; body: string; signal?: AbortSignal;
}) => Promise<StreamResponse>;
export type StreamOptions = { token: string; body?: unknown; signal?: AbortSignal; maxReconnects?: number };
export type StreamResult = { status: "done" | "canceled"; text: string; lastEventId: string; reconnects: number };

export async function streamAnswer(fetchFn: StreamFetch, url: string, opts: StreamOptions): Promise<StreamResult> {
  throw new Error("not implemented");
}
