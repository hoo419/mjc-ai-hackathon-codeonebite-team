import coursesData from "@/mocks/courses.json";
import type { Course } from "@/types";

// Mock 세션 상태 — 실제 백엔드가 붙기 전까지 메모리에 보관한다.
export const mockCourses: Course[] = coursesData as Course[];

export let enrolledCourseIds: string[] = ["CS301-01"];

export function setEnrolledCourseIds(ids: string[]) {
  enrolledCourseIds = ids;
}
