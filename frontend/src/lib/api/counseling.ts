import type {
  AptitudeAnalysisResult,
  CounselingRequestResult,
  CounselingSummary,
  CounselingTargetType,
} from "@/types";
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

// POST /counseling/analyze-aptitude - mpu.mjc.ac.kr(SMART CARE)은 로그인이
// 필수라 학생이 직접 로그인해서 확인한 검사 결과 원문을 붙여넣는다.
export function analyzeAptitude(rawText: string): Promise<AptitudeAnalysisResult> {
  return apiPost<AptitudeAnalysisResult>("/counseling/analyze-aptitude", { rawText });
}
