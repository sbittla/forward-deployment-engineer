export interface Schema<T> {
  parse(value: unknown, path?: string): T;
}

export class ValidationError extends Error {}

export class HttpError extends Error {
  status: number;
  constructor(status: number) {
    super(`HTTP ${status}`);
    this.status = status;
  }
}

export function str(): Schema<string> {
  throw new Error("not implemented");
}

export function num(): Schema<number> {
  throw new Error("not implemented");
}

export function bool(): Schema<boolean> {
  throw new Error("not implemented");
}

export function arr<T>(item: Schema<T>): Schema<T[]> {
  throw new Error("not implemented");
}

export function obj<S extends Record<string, Schema<unknown>>>(shape: S): Schema<{ [K in keyof S]: ReturnType<S[K]["parse"]> }> {
  throw new Error("not implemented");
}

export function optional<T>(inner: Schema<T>): Schema<T | undefined> {
  throw new Error("not implemented");
}

export function literal<T extends string>(...values: T[]): Schema<T> {
  throw new Error("not implemented");
}

export const TicketSchema = undefined as unknown as Schema<{
  id: number; title: string; priority: "low" | "normal" | "high" | "urgent"; tags: string[]; assignee?: string;
}>;

type FetchFn = (url: string, init?: { headers?: Record<string, string> }) => Promise<{ ok: boolean; status: number; json(): Promise<unknown> }>;

export function createClient(baseUrl: string, fetchFn: FetchFn) {
  throw new Error("not implemented");
}
