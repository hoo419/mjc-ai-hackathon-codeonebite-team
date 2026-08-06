import type { CourseCategory, CourseClassType, CourseStatus, Day } from "@/types";

export const dayLabel: Record<Day, string> = {
  MON: "월",
  TUE: "화",
  WED: "수",
  THU: "목",
  FRI: "금",
  SAT: "토",
  SUN: "일",
};

export const classTypeLabel: Record<CourseClassType, string> = {
  OFFLINE: "오프라인",
  ONLINE_LIVE: "온라인(실시간)",
  ONLINE_RECORDED: "온라인(녹화)",
  HYBRID: "혼합",
};

export const categoryLabel: Record<CourseCategory, string> = {
  GENERAL_COURSE: "교양과정",
  GENERAL_REQUIRED: "교양필수",
  GENERAL_ELECTIVE: "일반선택",
  MAJOR_COURSE: "전공과정",
  INTEGRATED_MAJOR: "통합전공교과",
};

export const statusLabel: Record<CourseStatus, string> = {
  OPEN: "신청 가능",
  FULL: "정원 마감",
  CANCELLED: "폐강",
  UPCOMING: "신청 예정",
  CLOSED: "신청 마감",
};

export const statusBadgeVariant: Record<
  CourseStatus,
  "default" | "secondary" | "destructive" | "outline"
> = {
  OPEN: "default",
  FULL: "secondary",
  CANCELLED: "destructive",
  UPCOMING: "outline",
  CLOSED: "outline",
};
