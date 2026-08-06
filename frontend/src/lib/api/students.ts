import type { Course, ScheduleEntry, Student } from "@/types";
import { apiGet } from "./client";

// GET /students/me
export function getMe(): Promise<{ student: Student }> {
  return apiGet<{ student: Student }>("/students/me");
}

// GET /students/me/courses
export function getMyCourses(): Promise<{ courses: Course[] }> {
  return apiGet<{ courses: Course[] }>("/students/me/courses");
}

// GET /students/me/schedule
export function getMySchedule(): Promise<{ schedule: ScheduleEntry[] }> {
  return apiGet<{ schedule: ScheduleEntry[] }>("/students/me/schedule");
}
