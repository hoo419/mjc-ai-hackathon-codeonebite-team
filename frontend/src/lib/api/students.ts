import type { Course, ScheduleEntry, Student } from "@/types";
import { apiGet, apiPatch } from "./client";

// GET /students/me
export function getMe(): Promise<{ student: Student }> {
  return apiGet<{ student: Student }>("/students/me");
}

// PATCH /students/me - 학생이 학교 포털에 직접 로그인해서 확인한 값을
// 우리 앱에 입력한다. 비밀번호/로그인 절차는 우리 앱이 전혀 다루지 않는다.
export function updateMe(profile: {
  department: string;
  grade: number;
  semester: number;
}): Promise<{ student: Student }> {
  return apiPatch<{ student: Student }>("/students/me", profile);
}

// GET /students/me/courses
export function getMyCourses(): Promise<{ courses: Course[] }> {
  return apiGet<{ courses: Course[] }>("/students/me/courses");
}

// GET /students/me/schedule
export function getMySchedule(): Promise<{ schedule: ScheduleEntry[] }> {
  return apiGet<{ schedule: ScheduleEntry[] }>("/students/me/schedule");
}
