"use client";

import { useState } from "react";
import Link from "next/link";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { NewStudentDeptNotice } from "@/components/new-student-dept-notice";
import { ProfileEditDialog } from "@/components/profile-edit-dialog";
import { useAsyncData } from "@/hooks/use-async-data";
import { getMe, getMySchedule } from "@/lib/api";
import { classTypeLabel, dayLabel } from "@/lib/labels";
import { getNextClass, getTodaySchedule } from "@/lib/schedule";
import type { Student } from "@/types";
import { CalendarDays, CalendarRange, DoorOpen, Megaphone, MessageCircle, Search } from "lucide-react";

// 학사공지/학사일정은 실시간으로 긁어와 재현하지 않고, 학교 홈페이지 원본
// 페이지로 바로 연결한다 - 학교 사이트 구조가 바뀌어도 우리 쪽이 깨지지
// 않고, 항상 원본 그대로다.
const SCHOOL_NOTICE_BOARD_URL = "https://www.mjc.ac.kr/bbs/data/list.do?menu_idx=169";
const SCHOOL_ACADEMIC_CALENDAR_URL = "https://www.mjc.ac.kr/collegeService/schedule.do?menu_idx=104";

export default function DashboardPage() {
  const { data: studentData, loading: studentLoading } = useAsyncData(() => getMe());
  const { data: scheduleData, loading: scheduleLoading } = useAsyncData(() => getMySchedule());
  const [studentOverride, setStudentOverride] = useState<Student | null>(null);

  const student = studentOverride ?? studentData?.student;
  const schedule = scheduleData?.schedule ?? [];
  const todaySchedule = getTodaySchedule(schedule);
  const nextClass = getNextClass(schedule);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Card>
        <CardContent className="flex items-center gap-4 py-2">
          {studentLoading || !student ? (
            <Skeleton className="h-12 w-12 rounded-full" />
          ) : (
            <Avatar className="h-12 w-12">
              <AvatarFallback>{student.name.slice(0, 1)}</AvatarFallback>
            </Avatar>
          )}
          <div className="flex-1">
            {studentLoading || !student ? (
              <>
                <Skeleton className="mb-2 h-4 w-24" />
                <Skeleton className="h-3 w-40" />
              </>
            ) : (
              <>
                <p className="font-heading text-sm font-semibold">{student.name}</p>
                <p className="text-xs text-muted-foreground">
                  {student.department} {student.grade}학년 {student.semester}학기
                </p>
              </>
            )}
          </div>
          {student && (
            <ProfileEditDialog student={student} onUpdated={setStudentOverride} />
          )}
        </CardContent>
      </Card>

      {student && student.grade === 1 && student.semester === 1 && (
        <NewStudentDeptNotice department={student.department} />
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">다음 수업</CardTitle>
          </CardHeader>
          <CardContent>
            {scheduleLoading ? (
              <Skeleton className="h-16 w-full" />
            ) : nextClass ? (
              <div className="space-y-1">
                <p className="font-medium">{nextClass.name}</p>
                <p className="text-sm text-muted-foreground">
                  {dayLabel[nextClass.day]} {nextClass.startTime}~{nextClass.endTime} ·{" "}
                  {nextClass.professor}
                </p>
                <p className="text-sm text-muted-foreground">
                  {nextClass.building ? `${nextClass.building} ${nextClass.room}` : (nextClass.classType ? classTypeLabel[nextClass.classType] : "온라인(방식 확인 안 됨)")}
                </p>
                {nextClass.room && (
                  <Button
                    render={<Link href="/rooms" />}
                    variant="link"
                    className="h-auto p-0 text-sm"
                  >
                    <DoorOpen className="h-3.5 w-3.5" /> 강의실 안내 보기
                  </Button>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">예정된 수업이 없습니다.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">오늘 시간표</CardTitle>
          </CardHeader>
          <CardContent>
            {scheduleLoading ? (
              <Skeleton className="h-16 w-full" />
            ) : todaySchedule.length === 0 ? (
              <p className="text-sm text-muted-foreground">오늘은 수업이 없습니다.</p>
            ) : (
              <ul className="space-y-2">
                {todaySchedule.map((entry, i) => (
                  <li key={`${entry.courseId}-${i}`} className="text-sm">
                    <span className="font-medium">{entry.startTime}</span> {entry.name}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Button
          render={<a href={SCHOOL_NOTICE_BOARD_URL} target="_blank" rel="noreferrer" />}
          variant="secondary"
          className="h-auto flex-col gap-1 py-4"
        >
          <Megaphone className="h-4 w-4" /> 학사공지
        </Button>
        <Button
          render={<a href={SCHOOL_ACADEMIC_CALENDAR_URL} target="_blank" rel="noreferrer" />}
          variant="secondary"
          className="h-auto flex-col gap-1 py-4"
        >
          <CalendarRange className="h-4 w-4" /> 학사일정
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Button render={<Link href="/courses" />} variant="secondary" className="h-auto flex-col gap-1 py-4">
          <Search className="h-4 w-4" /> 수강신청
        </Button>
        <Button render={<Link href="/counseling" />} variant="secondary" className="h-auto flex-col gap-1 py-4">
          <CalendarDays className="h-4 w-4" /> 상담
        </Button>
        <Button render={<Link href="/chat" />} variant="secondary" className="h-auto flex-col gap-1 py-4">
          <MessageCircle className="h-4 w-4" /> AI 비서
        </Button>
      </div>
    </div>
  );
}
