import { useEffect, useMemo, useRef, useState } from "react";

import { streamChatMessage } from "@/lib/streamChat";

import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";

let messageCounter = 0;

function nextMessageId() {
  messageCounter += 1;
  return `message-${messageCounter}`;
}

export default function ChatPanel() {
  const sessionId = useMemo(
    () => `session-${Math.random().toString(36).slice(2, 10)}`,
    [],
  );
  const [messages, setMessages] = useState([
    {
      id: nextMessageId(),
      role: "assistant",
      content: "I'm here — ask me to analyze a U.S. stock.",
      isStreaming: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const handleSubmit = async () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) {
      return;
    }

    const userMessage = {
      id: nextMessageId(),
      role: "user",
      content: trimmed,
      isStreaming: false,
    };
    const assistantMessageId = nextMessageId();

    setMessages((current) => [
      ...current,
      userMessage,
      {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        isStreaming: true,
      },
    ]);
    setInput("");
    setIsStreaming(true);

    await streamChatMessage(
      trimmed,
      (delta) => {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantMessageId
              ? {
                  ...message,
                  content: `${message.content}${delta}`,
                  isStreaming: true,
                }
              : message,
          ),
        );
      },
      () => {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantMessageId
              ? {
                  ...message,
                  isStreaming: false,
                }
              : message,
          ),
        );
        setIsStreaming(false);
      },
      () => {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantMessageId
              ? {
                  ...message,
                  content:
                    "Something interrupted the live stream. Please try again in a moment.",
                  isStreaming: false,
                }
              : message,
          ),
        );
        setIsStreaming(false);
      },
      sessionId,
    );
  };

  return (
    <section className="flex h-[calc(100vh-72px)] min-h-[720px] w-full max-w-[500px] flex-col overflow-hidden rounded-[28px] border border-[rgba(90,80,65,0.12)] bg-[rgba(255,255,255,0.52)] shadow-[0_22px_54px_rgba(49,39,26,0.07)] backdrop-blur-[18px]">
      <div
        ref={scrollRef}
        className="flex-1 space-y-5 overflow-y-auto px-6 py-7"
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
      </div>

      <div className="px-5 pb-5 pt-2">
        <ChatInput
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          disabled={isStreaming}
        />
      </div>
    </section>
  );
}
