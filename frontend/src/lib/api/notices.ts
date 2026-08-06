import type { Notice } from "@/types";
import { apiGet } from "./client";

// GET /notices
export function getNotices(): Promise<{ notices: Notice[] }> {
  return apiGet<{ notices: Notice[] }>("/notices");
}
