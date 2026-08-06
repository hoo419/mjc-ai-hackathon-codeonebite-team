import counselingData from "@/mocks/counseling.json";
import type { CounselingRequestResult, CounselingSummary, CounselingTargetType } from "@/types";

// GET /counseling/me
export async function getMyCounseling(): Promise<CounselingSummary> {
  return counselingData as CounselingSummary;
}

// POST /counseling/request
export async function requestCounseling(
  targetType: CounselingTargetType,
  message: string
): Promise<CounselingRequestResult> {
  void targetType;
  void message;
  return {
    success: true,
    requestId: `counsel-req-${Date.now()}`,
    status: "REQUESTED",
  };
}
