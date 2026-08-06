"use client";

import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useAsyncData } from "@/hooks/use-async-data";
import { usePreviewCourseIds } from "@/hooks/use-preview-course-ids";
import { getCourses, getMySchedule } from "@/lib/api";
import { classTypeLabel, dayLabel } from "@/lib/labels";
import { getNextClass, hasConflict } from "@/lib/schedule";
import { toMinutes, todayAsDay } from "@/lib/time";
import { cn } from "@/lib/utils";
import type { CourseStatus, Day } from "@/types";

const DAY_COLUMNS: Day[] = ["MON", "TUE", "WED", "THU", "FRI"];
const GRID_START = 9 * 60;
const GRID_END = 18 * 60;
const HOUR_HEIGHT = 56;
const HOURS = Array.from({ length: (GRID_END - GRID_START) / 60 + 1 }, (_, i) => 9 + i);

interface Block {
  key: string;
  courseId: string;
  day: Day;
  startTime: string;
  endTime: string;
  name: string;
  professor: string;
  classType: string;
  building: string | null;
  room: string | null;
  status?: CourseStatus;
  isPreview: boolean;
}

function computeConflictKeys(blocks: Block[]): Set<string> {
  const conflicts = new Set<string>();
  for (let i = 0; i < blocks.length; i++) {
    for (let j = i + 1; j < blocks.length; j++) {
      if (blocks[i].courseId === blocks[j].courseId) continue;
      if (hasConflict(blocks[i], blocks[j])) {
        conflicts.add(blocks[i].key);
        conflicts.add(blocks[j].key);
      }
    }
  }
  return conflicts;
}

export default function SchedulePage() {
  const { data: scheduleData, loading } = useAsyncData(() => getMySchedule());
  const { data: coursesData } = useAsyncData(() => getCourses());
  const previewIds = usePreviewCourseIds();
  const [selected, setSelected] = useState<Block | null>(null);

  const schedule = scheduleData?.schedule ?? [];
  const today = todayAsDay();
  const nextClass = getNextClass(schedule);

  const blocks: Block[] = useMemo(() => {
    const scheduleList = scheduleData?.schedule ?? [];
    const courseList = coursesData?.courses ?? [];

    const enrolledBlocks: Block[] = scheduleList.map((e) => ({
      key: `enrolled-${e.courseId}`,
      courseId: e.courseId,
      day: e.day,
      startTime: e.startTime,
      endTime: e.endTime,
      name: e.name,
      professor: e.professor,
      classType: e.classType,
      building: e.building,
      room: e.room,
      isPreview: false,
    }));

    const previewBlocks: Block[] = previewIds
      .map((id) => courseList.find((c) => c.id === id))
      .filter((c): c is NonNullable<typeof c> => !!c)
      .map((c) => ({
        key: `preview-${c.id}`,
        courseId: c.id,
        day: c.day,
        startTime: c.startTime,
        endTime: c.endTime,
        name: c.name,
        professor: c.professor,
        classType: c.classType,
        building: c.building,
        room: c.room,
        status: c.status,
        isPreview: true,
      }));

    return [...enrolledBlocks, ...previewBlocks];
  }, [scheduleData, coursesData, previewIds]);

  const conflictKeys = computeConflictKeys(blocks);

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="font-heading text-lg font-semibold">스마트 시간표</h1>
        {nextClass && (
          <p className="text-xs text-muted-foreground">
            다음 수업: {dayLabel[nextClass.day]} {nextClass.startTime} {nextClass.name}
          </p>
        )}
      </div>

      {loading ? (
        <Skeleton className="h-[500px] w-full" />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <div className="grid min-w-[640px] grid-cols-[3rem_repeat(5,1fr)]">
            <div />
            {DAY_COLUMNS.map((day) => (
              <div
                key={day}
                className={cn(
                  "border-b border-l border-border py-2 text-center text-sm font-medium",
                  day === today && "bg-secondary text-secondary-foreground"
                )}
              >
                {dayLabel[day]}
              </div>
            ))}

            <div className="relative" style={{ height: HOURS.length * HOUR_HEIGHT }}>
              {HOURS.map((h) => (
                <div
                  key={h}
                  className="absolute right-1 -translate-y-2 text-[11px] text-muted-foreground"
                  style={{ top: (h * 60 - GRID_START) / 60 * HOUR_HEIGHT }}
                >
                  {h}
                </div>
              ))}
            </div>

            {DAY_COLUMNS.map((day) => (
              <div
                key={day}
                className="relative border-l border-border"
                style={{ height: HOURS.length * HOUR_HEIGHT }}
              >
                {HOURS.map((h) => (
                  <div
                    key={h}
                    className="absolute w-full border-t border-border/50"
                    style={{ top: (h * 60 - GRID_START) / 60 * HOUR_HEIGHT }}
                  />
                ))}

                {blocks
                  .filter((b) => b.day === day)
                  .map((b) => {
                    const top = ((toMinutes(b.startTime) - GRID_START) / 60) * HOUR_HEIGHT;
                    const height = ((toMinutes(b.endTime) - toMinutes(b.startTime)) / 60) * HOUR_HEIGHT;
                    const conflicted = conflictKeys.has(b.key);
                    return (
                      <button
                        key={b.key}
                        onClick={() => setSelected(b)}
                        className={cn(
                          "absolute inset-x-0.5 overflow-hidden rounded-md p-1 text-left text-[11px] leading-tight",
                          b.isPreview
                            ? "border border-dashed border-primary bg-primary/10"
                            : "bg-secondary text-secondary-foreground",
                          conflicted && "ring-2 ring-destructive"
                        )}
                        style={{ top, height: Math.max(height, 20) }}
                      >
                        <p className="truncate font-medium">{b.name}</p>
                        <p className="truncate text-muted-foreground">
                          {b.startTime}-{b.endTime}
                        </p>
                        {conflicted && (
                          <Badge variant="destructive" className="mt-0.5 h-4 px-1 text-[9px]">
                            충돌
                          </Badge>
                        )}
                      </button>
                    );
                  })}
              </div>
            ))}
          </div>
        </div>
      )}

      <Dialog open={!!selected} onOpenChange={(open) => !open && setSelected(null)}>
        <DialogContent>
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle>{selected.name}</DialogTitle>
                <DialogDescription>
                  {selected.isPreview ? "시간표 미리보기 (아직 신청되지 않음)" : "신청된 과목"}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-1 text-sm">
                <p>담당교수: {selected.professor}</p>
                <p>
                  시간: {dayLabel[selected.day]} {selected.startTime}~{selected.endTime}
                </p>
                <p>
                  수업방식: {classTypeLabel[selected.classType as keyof typeof classTypeLabel]}
                </p>
                <p>
                  장소: {selected.building ? `${selected.building} ${selected.room}호` : "온라인"}
                </p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
