// API_CONTRACT.md 기준 타입. 필드/Enum을 임의로 바꾸지 않는다.

export type CourseClassType =
  | "OFFLINE"
  | "ONLINE_LIVE"
  | "ONLINE_RECORDED"
  | "HYBRID";

export type CourseStatus =
  | "OPEN"
  | "FULL"
  | "CANCELLED"
  | "UPCOMING"
  | "CLOSED";

export type CourseCategory =
  | "GENERAL_COURSE"
  | "GENERAL_REQUIRED"
  | "GENERAL_ELECTIVE"
  | "MAJOR_COURSE"
  | "INTEGRATED_MAJOR";

export type Day = "MON" | "TUE" | "WED" | "THU" | "FRI" | "SAT" | "SUN";

export interface Session {
  day: Day;
  startTime: string; // "13:00"
  endTime: string; // "15:50"
  building: string | null;
  room: string | null;
}

export interface EligibleDept {
  code: string;
  name: string;
}

export interface Course {
  id: string;
  name: string;
  professor: string;
  credits: number;
  category: CourseCategory;
  classType: CourseClassType | null;
  sessions: Session[];
  targetGrade: number;
  eligibleDepts: EligibleDept[];
  capacity: number;
  enrolled: number;
  status: CourseStatus;
  lastUpdated: string; // ISO 8601
}

export interface Student {
  id: string;
  name: string;
  department: string;
  grade: number;
  semester: number;
}

export interface ScheduleEntry {
  courseId: string;
  name: string;
  professor: string;
  classType: CourseClassType | null;
  day: Day;
  startTime: string;
  endTime: string;
  building: string | null;
  room: string | null;
}


export interface CounselingSummary {
  careerSummary: string;
  personalitySummary: string;
  lastCounselingAt: string;
}

export type CounselingTargetType =
  | "ADVISOR"
  | "CAREER_COUNSELOR"
  | "DEPARTMENT_OFFICE";

export interface CounselingRequestResult {
  success: true;
  requestId: string;
  status: "REQUESTED";
}

export interface AptitudeAnalysisResult {
  summary: string;
  insights: string[];
}

export interface Building {
  id: string;
  name: string;
}

export interface Room {
  id: string;
  building: string;
  floor: number;
  room: string;
  directions: string[];
}

export interface ChatSource {
  title: string;
  url: string;
}

export interface ChatAction {
  type: "VIEW_COURSE" | string;
  label: string;
  targetId: string;
}

export interface ChatResponse {
  answer: string;
  sources?: ChatSource[];
  courses?: Course[];
  actions?: ChatAction[];
}

export type EnrollmentErrorCode =
  | "COURSE_FULL"
  | "COURSE_CANCELLED"
  | "ENROLLMENT_CLOSED"
  | "TIME_CONFLICT"
  | "NOT_ELIGIBLE"
  | "ALREADY_ENROLLED"
  | "COURSE_NOT_FOUND";

export interface ApiError {
  error: {
    code: EnrollmentErrorCode | string;
    message: string;
  };
}

export interface EnrollmentSuccess {
  success: true;
  enrollment: {
    courseId: string;
    status: "ENROLLED";
  };
}

export interface EnrollmentFailure {
  success: false;
  error: {
    code: EnrollmentErrorCode;
    message: string;
  };
}

export type EnrollmentResult = EnrollmentSuccess | EnrollmentFailure;
