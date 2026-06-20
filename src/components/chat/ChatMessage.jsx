function StreamingDots() {
  return (
    <span className="chat-dots inline-flex items-center gap-1 align-middle">
      <span className="chat-dot h-1.5 w-1.5 rounded-full bg-[#B9805D]" />
      <span className="chat-dot h-1.5 w-1.5 rounded-full bg-[#B9805D]" />
      <span className="chat-dot h-1.5 w-1.5 rounded-full bg-[#B9805D]" />
    </span>
  );
}

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "max-w-[82%] rounded-[22px] border border-[rgba(168,95,43,0.12)] bg-[rgba(204,120,92,0.14)] px-4 py-3 text-[15px] leading-[1.65] text-[#3D3D3A]"
            : "max-w-[92%] px-1 py-1 text-[15px] leading-[1.75] text-[#3D3D3A]"
        }
      >
        <div className="whitespace-pre-wrap break-words">
          {message.content}
          {message.isStreaming && <StreamingDots />}
        </div>
      </div>
    </div>
  );
}
