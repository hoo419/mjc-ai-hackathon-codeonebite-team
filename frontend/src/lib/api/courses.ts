import type { Course, CourseClassType, CourseCategory, CourseStatus } from "@/types";
import { mockCourses } from "./store";

export interface GetCoursesParams {
  status?: CourseStatus;
  classType?: CourseClassType;
  category?: CourseCategory;
  search?: string;
}

// GET /courses
export async function getCourses(params: GetCoursesParams = {}): Promise<{ courses: Course[] }> {
  let courses = mockCourses;
  if (params.status) courses = courses.filter((c) => c.status === params.status);
  if (params.classType) courses = courses.filter((c) => c.classType === params.classType);
  if (params.category) courses = courses.filter((c) => c.category === params.category);
  if (params.search) {
    const q = params.search.toLowerCase();
    courses = courses.filter(
      (c) => c.name.toLowerCase().includes(q) || c.professor.toLowerCase().includes(q)
    );
  }
  return { courses };
}

// GET /courses/{courseId}
export async function getCourse(courseId: string): Promise<{ course: Course | null }> {
  const course = mockCourses.find((c) => c.id === courseId) ?? null;
  return { course };
}
