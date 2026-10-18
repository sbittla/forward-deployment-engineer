export type SSEEvent = { event: string; data: string };

export class Utf8Chunker {
  private decoder = new TextDecoder("utf-8");
  push(bytes: Uint8Array): string {
    return this.decoder.decode(bytes, { stream: true });
  }
  end(): string {
    return this.decoder.decode();
  }
}

export class SSEParser {
  private buffer = "";
  private event = "message";
  private data: string[] = [];

  private line(raw: string, out: SSEEvent[]) {
    if (raw === "") {
      if (this.data.length) out.push({ event: this.event, data: this.data.join("\n") });
      this.event = "message";
      this.data = [];
      return;
    }
    if (raw.startsWith(":")) return;
    const idx = raw.indexOf(":");
    const field = idx === -1 ? raw : raw.slice(0, idx);
    let value = idx === -1 ? "" : raw.slice(idx + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") this.event = value;
    else if (field === "data") this.data.push(value);
  }

  push(text: string): SSEEvent[] {
    this.buffer += text;
    const out: SSEEvent[] = [];
    let nl: number;
    while ((nl = this.buffer.indexOf("\n")) !== -1) {
      let raw = this.buffer.slice(0, nl);
      this.buffer = this.buffer.slice(nl + 1);
      if (raw.endsWith("\r")) raw = raw.slice(0, -1);
      this.line(raw, out);
    }
    return out;
  }

  end(): SSEEvent[] {
    const out: SSEEvent[] = [];
    if (this.buffer) {
      this.line(this.buffer.replace(/\r$/, ""), out);
      this.buffer = "";
    }
    this.line("", out);
    return out;
  }
}

export function accumulateText(events: SSEEvent[]): string {
  let text = "";
  for (const ev of events) {
    if (ev.event === "message_stop") break;
    if (ev.event === "error") throw new Error(JSON.parse(ev.data).error?.message ?? "stream error");
    if (ev.event === "content_block_delta") {
      const d = JSON.parse(ev.data).delta;
      if (d?.type === "text_delta") text += d.text;
    }
  }
  return text;
}
