"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { CourseCard } from "@/components/course-card";
import { useAsyncData } from "@/hooks/use-async-data";
import { usePreviewCourseIds } from "@/hooks/use-preview-course-ids";
import { enroll, getCourses, getMyCourses } from "@/lib/api";
import { categoryLabel, classTypeLabel, statusLabel } from "@/lib/labels";
import { togglePreview } from "@/lib/preview-store";
import type { CourseCategory, CourseClassType, CourseStatus } from "@/types";

export default function CoursesPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<CourseStatus | "ALL">("ALL");
  const [classType, setClassType] = useState<CourseClassType | "ALL">("ALL");
  const [category, setCategory] = useState<CourseCategory | "ALL">("ALL");
  const [refreshKey, setRefreshKey] = useState(0);
  const [enrollingId, setEnrollingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<string, { ok: boolean; message: string }>>({});

  const previewIds = usePreviewCourseIds();

  const { data: coursesData, loading } = useAsyncData(
    () =>
      getCourses({
        search: search || undefined,
        status: status === "ALL" ? undefined : status,
        classType: classType === "ALL" ? undefined : classType,
        category: category === "ALL" ? undefined : category,
      }),
    [search, status, classType, category, refreshKey]
  );
  const { data: myCoursesData } = useAsyncData(() => getMyCourses(), [refreshKey]);

  const enrolledIds = new Set((myCoursesData?.courses ?? []).map((c) => c.id));
  const courses = coursesData?.courses ?? [];

  async function handleAddToSchedule(courseId: string) {
    setEnrollingId(courseId);
    const result = await enroll(courseId);
    setFeedback((prev) => ({
      ...prev,
      [courseId]: result.success
        ? { ok: true, message: "내 시간표에 추가되었습니다." }
        : { ok: false, message: result.error.message },
    }));
    setEnrollingId(null);
    setRefreshKey((k) => k + 1);
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-4">
      <div>
        <h1 className="font-heading text-lg font-semibold">수강과목 검색</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          실제 수강신청은{" "}
          <a
            href="https://sugang.mjc.ac.kr/"
            target="_blank"
            rel="noreferrer"
            className="underline underline-offset-2 hover:text-foreground"
          >
            명지전문대학 수강신청시스템
          </a>
          에서 진행해 주세요. 여기서는 신청을 마친 과목을 골라 담아두면, 겹치는
          시간이 없는지·강의실이 어딘지 내 시간표에서 바로 확인할 수 있습니다.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="과목명, 교수명 검색"
          className="w-full sm:w-56"
        />
        <Select value={status} onValueChange={(v) => setStatus(v as CourseStatus | "ALL")}>
          <SelectTrigger size="sm">
            <SelectValue placeholder="상태" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">전체 상태</SelectItem>
            {(Object.keys(statusLabel) as CourseStatus[]).map((s) => (
              <SelectItem key={s} value={s}>
                {statusLabel[s]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={classType} onValueChange={(v) => setClassType(v as CourseClassType | "ALL")}>
          <SelectTrigger size="sm">
            <SelectValue placeholder="수업방식" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">전체 수업방식</SelectItem>
            {(Object.keys(classTypeLabel) as CourseClassType[]).map((c) => (
              <SelectItem key={c} value={c}>
                {classTypeLabel[c]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={category} onValueChange={(v) => setCategory(v as CourseCategory | "ALL")}>
          <SelectTrigger size="sm">
            <SelectValue placeholder="구분" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">전체 구분</SelectItem>
            {(Object.keys(categoryLabel) as CourseCategory[]).map((c) => (
              <SelectItem key={c} value={c}>
                {categoryLabel[c]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-40 w-full" />
          ))}
        </div>
      ) : courses.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">조건에 맞는 과목이 없습니다.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {courses.map((course) => {
            const isEnrolled = enrolledIds.has(course.id);
            const isPreview = previewIds.includes(course.id);
            const cardFeedback = feedback[course.id];
            return (
              <CourseCard
                key={course.id}
                course={course}
                footer={
                  <div className="flex w-full flex-col gap-1.5">
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => togglePreview(course.id)}
                      >
                        {isPreview ? "미리보기 해제" : "시간표에 넣어보기"}
                      </Button>
                      <Button
                        size="sm"
                        className="flex-1"
                        disabled={enrollingId === course.id || isEnrolled}
                        onClick={() => handleAddToSchedule(course.id)}
                      >
                        {isEnrolled ? "추가됨" : "신청한 과목 추가"}
                      </Button>
                    </div>
                    {cardFeedback && (
                      <p className={cardFeedback.ok ? "text-xs text-foreground" : "text-xs text-destructive"}>
                        {cardFeedback.message}
                      </p>
                    )}
                  </div>
                }
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
