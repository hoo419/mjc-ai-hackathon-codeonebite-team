import noticesData from "@/mocks/notices.json";
import type { Notice } from "@/types";

// GET /notices
export async function getNotices(): Promise<{ notices: Notice[] }> {
  return { notices: noticesData as Notice[] };
}
