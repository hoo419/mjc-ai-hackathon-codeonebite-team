import studentData from "@/mocks/student.json";
import type { Course, ScheduleEntry, Student } from "@/types";
import { enrolledCourseIds, mockCourses } from "./store";

// GET /students/me
export async function getMe(): Promise<{ student: Student }> {
  return { student: studentData as Student };
}

// GET /students/me/courses
export async function getMyCourses(): Promise<{ courses: Course[] }> {
  const courses = mockCourses.filter((c) => enrolledCourseIds.includes(c.id));
  return { courses };
}

// GET /students/me/schedule
export async function getMySchedule(): Promise<{ schedule: ScheduleEntry[] }> {
  const schedule: ScheduleEntry[] = mockCourses
    .filter((c) => enrolledCourseIds.includes(c.id))
    .map((c) => ({
      courseId: c.id,
      name: c.name,
      professor: c.professor,
      classType: c.classType,
      day: c.day,
      startTime: c.startTime,
      endTime: c.endTime,
      building: c.building,
      room: c.room,
    }));
  return { schedule };
}
