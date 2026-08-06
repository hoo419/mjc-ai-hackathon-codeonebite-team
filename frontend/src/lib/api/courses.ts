import type { Course, CourseCategory, CourseClassType, CourseStatus } from "@/types";
import { apiGet } from "./client";

export interface GetCoursesParams {
  status?: CourseStatus;
  classType?: CourseClassType;
  category?: CourseCategory;
  search?: string;
}

// GET /courses
export async function getCourses(params: GetCoursesParams = {}): Promise<{ courses: Course[] }> {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.classType) query.set("classType", params.classType);
  if (params.category) query.set("category", params.category);
  if (params.search) query.set("search", params.search);

  const qs = query.toString();
  return apiGet<{ courses: Course[] }>(`/courses${qs ? `?${qs}` : ""}`);
}

// GET /courses/{courseId}
export async function getCourse(courseId: string): Promise<{ course: Course | null }> {
  try {
    return await apiGet<{ course: Course }>(`/courses/${courseId}`);
  } catch {
    return { course: null };
  }
}
