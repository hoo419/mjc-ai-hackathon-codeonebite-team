import type { EnrollmentResult } from "@/types";
import { hasConflict } from "@/lib/schedule";
import { enrolledCourseIds, mockCourses, setEnrolledCourseIds } from "./store";

function hasTimeConflict(courseId: string): boolean {
  const target = mockCourses.find((c) => c.id === courseId);
  if (!target) return false;

  return enrolledCourseIds.some((id) => {
    const enrolled = mockCourses.find((c) => c.id === id);
    return !!enrolled && hasConflict(target, enrolled);
  });
}

// POST /enrollment
export async function enroll(courseId: string): Promise<EnrollmentResult> {
  const course = mockCourses.find((c) => c.id === courseId);

  if (!course) {
    return { success: false, error: { code: "COURSE_NOT_FOUND", message: "과목을 찾을 수 없습니다." } };
  }
  if (enrolledCourseIds.includes(courseId)) {
    return { success: false, error: { code: "ALREADY_ENROLLED", message: "이미 신청한 과목입니다." } };
  }
  if (course.status === "CANCELLED") {
    return { success: false, error: { code: "COURSE_CANCELLED", message: "폐강된 과목입니다." } };
  }
  if (course.status === "UPCOMING" || course.status === "CLOSED") {
    return { success: false, error: { code: "ENROLLMENT_CLOSED", message: "수강신청 기간이 아닙니다." } };
  }
  if (course.status === "FULL" || course.enrolled >= course.capacity) {
    return { success: false, error: { code: "COURSE_FULL", message: "수강 정원이 마감되었습니다." } };
  }
  if (hasTimeConflict(courseId)) {
    return { success: false, error: { code: "TIME_CONFLICT", message: "기존 시간표와 시간이 겹칩니다." } };
  }

  course.enrolled += 1;
  if (course.enrolled >= course.capacity) course.status = "FULL";
  setEnrolledCourseIds([...enrolledCourseIds, courseId]);

  return { success: true, enrollment: { courseId, status: "ENROLLED" } };
}

// DELETE /enrollment/{courseId}
export async function unenroll(courseId: string): Promise<{ success: true }> {
  const course = mockCourses.find((c) => c.id === courseId);
  if (course && enrolledCourseIds.includes(courseId)) {
    course.enrolled = Math.max(0, course.enrolled - 1);
    if (course.status === "FULL" && course.enrolled < course.capacity) course.status = "OPEN";
  }
  setEnrolledCourseIds(enrolledCourseIds.filter((id) => id !== courseId));
  return { success: true };
}
