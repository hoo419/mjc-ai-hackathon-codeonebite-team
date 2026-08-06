import type { EnrollmentResult } from "@/types";
import { apiDelete, apiPost } from "./client";

// POST /enrollment
export function enroll(courseId: string): Promise<EnrollmentResult> {
  return apiPost<EnrollmentResult>("/enrollment", { courseId });
}

// DELETE /enrollment/{courseId}
export function unenroll(courseId: string): Promise<{ success: true }> {
  return apiDelete<{ success: true }>(`/enrollment/${courseId}`);
}
