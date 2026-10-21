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
