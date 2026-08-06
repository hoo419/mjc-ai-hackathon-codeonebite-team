import type {
  AptitudeAnalysisResult,
  CounselingRequestResult,
  CounselingSummary,
  CounselingTargetType,
} from "@/types";
import { apiGet, apiPost } from "./client";

// GET /counseling/me - 진로적성검사 결과는 학생이 mpu.mjc.ac.kr에 직접
// 로그인해서 붙여넣어야만 존재하는 데이터라, 아직 그렇게 한 적 없으면
// 백엔드가 404(COUNSELING_SUMMARY_NOT_FOUND)를 준다. 화면에서는 에러가
// 아니라 "아직 결과 없음" 상태로 다뤄야 하므로 null로 바꿔서 돌려준다.
export async function getMyCounseling(): Promise<CounselingSummary | null> {
  try {
    return await apiGet<CounselingSummary>("/counseling/me");
  } catch {
    return null;
  }
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
