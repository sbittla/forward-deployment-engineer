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

function fail(path: string, what: string): never {
  throw new ValidationError(`${path}: expected ${what}`);
}

export function str(): Schema<string> {
  return { parse: (v, path = "$") => (typeof v === "string" ? v : fail(path, "string")) };
}

export function num(): Schema<number> {
  return { parse: (v, path = "$") => (typeof v === "number" && Number.isFinite(v) ? v : fail(path, "number")) };
}

export function bool(): Schema<boolean> {
  return { parse: (v, path = "$") => (typeof v === "boolean" ? v : fail(path, "boolean")) };
}

export function arr<T>(item: Schema<T>): Schema<T[]> {
  return {
    parse(v, path = "$") {
      if (!Array.isArray(v)) fail(path, "array");
      return v.map((x, i) => item.parse(x, `${path}[${i}]`));
    },
  };
}

export function obj<S extends Record<string, Schema<unknown>>>(shape: S): Schema<{ [K in keyof S]: ReturnType<S[K]["parse"]> }> {
  return {
    parse(v, path = "$") {
      if (typeof v !== "object" || v === null || Array.isArray(v)) fail(path, "object");
      const src = v as Record<string, unknown>;
      const out: Record<string, unknown> = {};
      for (const key of Object.keys(shape)) out[key] = shape[key].parse(src[key], `${path}.${key}`);
      return out as { [K in keyof S]: ReturnType<S[K]["parse"]> };
    },
  };
}

export function optional<T>(inner: Schema<T>): Schema<T | undefined> {
  return { parse: (v, path = "$") => (v === undefined ? undefined : inner.parse(v, path)) };
}

export function literal<T extends string>(...values: T[]): Schema<T> {
  return {
    parse: (v, path = "$") => ((values as unknown[]).includes(v) ? (v as T) : fail(path, `one of ${values.join("|")}`)),
  };
}

export const TicketSchema = obj({
  id: num(),
  title: str(),
  priority: literal("low", "normal", "high", "urgent"),
  tags: arr(str()),
  assignee: optional(str()),
});

type FetchFn = (url: string, init?: { headers?: Record<string, string> }) => Promise<{ ok: boolean; status: number; json(): Promise<unknown> }>;

export function createClient(baseUrl: string, fetchFn: FetchFn) {
  const base = baseUrl.replace(/\/+$/, "");
  return {
    async getTicket(id: number) {
      const res = await fetchFn(`${base}/tickets/${id}`, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new HttpError(res.status);
      return TicketSchema.parse(await res.json());
    },
  };
}
