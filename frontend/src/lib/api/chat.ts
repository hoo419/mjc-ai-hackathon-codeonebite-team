import type { ChatResponse } from "@/types";
import { apiPost } from "./client";

// POST /chat
export function sendChatMessage(message: string): Promise<ChatResponse> {
  return apiPost<ChatResponse>("/chat", { message });
}
