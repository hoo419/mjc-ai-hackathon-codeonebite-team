import type { CounselingRequestResult, CounselingSummary, CounselingTargetType } from "@/types";
import { apiGet, apiPost } from "./client";

// GET /counseling/me
export function getMyCounseling(): Promise<CounselingSummary> {
  return apiGet<CounselingSummary>("/counseling/me");
}

// POST /counseling/request
export function requestCounseling(
  targetType: CounselingTargetType,
  message: string
): Promise<CounselingRequestResult> {
  return apiPost<CounselingRequestResult>("/counseling/request", { targetType, message });
}
