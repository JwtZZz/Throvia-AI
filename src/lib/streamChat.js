const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function sleep(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function buildMockResponse(message) {
  const prompt = message.trim() || "the requested stock";

  return [
    `I’m looking at ${prompt}.`,
    "",
    "Here’s the first-pass research framing:",
    "- Market data and recent price movement will anchor the context.",
    "- News sentiment will help separate narrative noise from meaningful catalysts.",
    "- Financial quality, technical signals, and risk factors will be synthesized into one view.",
    "",
    "When the live backend stream is connected, this panel will progressively render the full multi-agent response.",
  ].join("\n");
}

function parseSSEChunk(buffer, onDelta, onDone) {
  const parts = buffer.split("\n\n");
  const remainder = parts.pop() ?? "";

  for (const part of parts) {
    const lines = part
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    let eventName = "message";
    const dataLines = [];

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventName = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trim());
      }
    }

    const data = dataLines.join("\n");
    if (!data) {
      continue;
    }

    if (eventName === "done") {
      onDone?.();
      continue;
    }

    try {
      const parsed = JSON.parse(data);
      if (typeof parsed?.delta === "string" && parsed.delta) {
        onDelta(parsed.delta);
      }
      if (parsed?.done) {
        onDone?.();
      }
    } catch {
      onDelta(data);
    }
  }

  return remainder;
}

async function streamMockMessage(message, onDelta, onDone) {
  const mockText = buildMockResponse(message);
  const segments = mockText.match(/.{1,18}(\s|$)|\n/g) || [mockText];

  for (const segment of segments) {
    await sleep(55);
    onDelta(segment === "\n" ? "\n" : segment);
  }

  onDone?.();
}

export async function streamChatMessage(
  message,
  onDelta,
  onDone,
  onError,
  sessionId = "default",
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`);
    }

    const contentType = response.headers.get("content-type") || "";
    const isSSE = contentType.includes("text/event-stream");
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      if (!chunk) {
        continue;
      }

      if (isSSE) {
        buffer += chunk;
        buffer = parseSSEChunk(buffer, onDelta, onDone);
      } else {
        onDelta(chunk);
      }
    }

    if (isSSE && buffer.trim()) {
      parseSSEChunk(`${buffer}\n\n`, onDelta, onDone);
    }

    onDone?.();
  } catch (error) {
    try {
      await streamMockMessage(message, onDelta, onDone);
    } catch (mockError) {
      onError?.(mockError || error);
    }
  }
}
