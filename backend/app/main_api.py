from __future__ import annotations

import asyncio
import json
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.graph.state import build_initial_state
from app.graph.workflow import build_workflow


app = FastAPI(title="AnthroVest AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = build_workflow()


class ChatStreamRequest(BaseModel):
    message: str
    session_id: str = "default"


def _chunk_text(text: str) -> Iterable[str]:
    clean = text.strip()
    if not clean:
        return ["No report was produced."]

    chunks = []
    current = []
    current_length = 0

    for token in clean.split():
        token_length = len(token) + 1
        if current and current_length + token_length > 42:
            chunks.append(" ".join(current) + " ")
            current = [token]
            current_length = len(token)
        else:
            current.append(token)
            current_length += token_length

    if current:
        chunks.append(" ".join(current))

    return chunks


async def _build_report(message: str, session_id: str) -> str:
    initial_state = build_initial_state(
        user_input=message,
        user_id="api-user",
        session_id=session_id,
    )
    final_state = await asyncio.to_thread(workflow.invoke, initial_state)
    return final_state.get("final_report") or "No report was produced."


@app.get("/api/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/api/chat/stream")
async def chat_stream(payload: ChatStreamRequest) -> StreamingResponse:
    async def event_stream():
      try:
          report = await _build_report(payload.message, payload.session_id)
          for chunk in _chunk_text(report):
              yield (
                  "event: token\n"
                  f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
              )
              await asyncio.sleep(0.03)

          yield "event: done\ndata: {\"done\": true}\n\n"
      except Exception as exc:  # pragma: no cover - defensive API fallback
          error_chunk = json.dumps(
              {"delta": f"Streaming error: {str(exc)}"},
              ensure_ascii=False,
          )
          yield f"event: token\ndata: {error_chunk}\n\n"
          yield "event: done\ndata: {\"done\": true}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
