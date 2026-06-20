import { useEffect, useRef } from "react";

export default function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled,
}) {
  const textareaRef = useRef(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = "0px";
    textarea.style.height = `${Math.max(52, Math.min(textarea.scrollHeight, 160))}px`;
  }, [value]);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="rounded-[24px] border border-[rgba(90,80,65,0.12)] bg-[rgba(255,255,255,0.6)] p-3 shadow-[0_16px_36px_rgba(61,52,41,0.05)] backdrop-blur-[16px]">
      <div className="flex items-center gap-3">
        <button
          type="button"
          className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-[rgba(90,80,65,0.12)] bg-[rgba(250,249,245,0.92)] text-[1.2rem] leading-none text-[#6C6A64] transition-colors duration-200 hover:bg-[rgba(245,240,232,0.96)]"
          aria-label="Add"
        >
          +
        </button>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask AnthroVest to analyze NVDA, TSLA, AAPL..."
          rows={1}
          className="min-h-[52px] flex-1 resize-none border-0 bg-transparent px-0 py-[12px] text-[15px] leading-[1.55] text-[#252523] outline-none placeholder:text-[#8E8B82]"
          style={{ overflow: "hidden" }}
        />

        <button
          type="button"
          onClick={onSubmit}
          disabled={disabled || !value.trim()}
          className="inline-flex h-11 min-w-[104px] shrink-0 items-center justify-center rounded-[16px] bg-[#C8793E] px-4 text-sm font-medium leading-none text-white shadow-[0_12px_28px_rgba(169,88,62,0.22)] transition-all duration-200 hover:-translate-y-0.5 hover:bg-[#B96E3A] disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-[#E6DFD8] disabled:text-[#8E8B82] disabled:shadow-none"
        >
          Send
        </button>
      </div>
    </div>
  );
}
