"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAsyncData } from "@/hooks/use-async-data";
import { getMySchedule, getRoom, roomIdFor } from "@/lib/api";
import { dayLabel } from "@/lib/labels";
import { getNextClass } from "@/lib/schedule";
import { cn } from "@/lib/utils";
import type { ScheduleEntry } from "@/types";

// 현재 데이터셋은 246개 실데이터 과목 전부 building이 null이라(원본이 "공502"
// 같은 축약 코드뿐이라 정식 건물명을 지어내지 않기로 함), 아래 필터는 항상
// 빈 배열을 반환한다. 필터 로직 자체의 버그가 아니라 데이터 한계이니 주의.
// building을 채우려면 별도의 건물명 매핑 데이터가 필요하다 (out of scope).
function uniqueRoomEntries(schedule: ScheduleEntry[]): ScheduleEntry[] {
  const seen = new Set<string>();
  return schedule.filter((e) => {
    if (!e.building || !e.room) return false;
    const key = `${e.building}-${e.room}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export default function RoomsPage() {
  const { data: scheduleData, loading: scheduleLoading } = useAsyncData(() => getMySchedule());
  const schedule = scheduleData?.schedule ?? [];
  const roomEntries = uniqueRoomEntries(schedule);
  const nextClass = getNextClass(schedule);

  const [manualKey, setManualKey] = useState<string | null>(null);
  const defaultKey =
    nextClass?.building && nextClass.room ? `${nextClass.building}-${nextClass.room}` : null;
  const selectedKey = manualKey ?? defaultKey;

  const selectedEntry = roomEntries.find((e) => `${e.building}-${e.room}` === selectedKey) ?? null;
  const selectedRoomId =
    selectedEntry?.building && selectedEntry.room ? roomIdFor(selectedEntry.building, selectedEntry.room) : null;

  const { data: roomData, loading: roomLoading } = useAsyncData(
    () => (selectedRoomId ? getRoom(selectedRoomId) : Promise.resolve({ room: null })),
    [selectedRoomId]
  );
  const room = roomData?.room ?? null;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <h1 className="font-heading text-lg font-semibold">강의실 안내</h1>

      {scheduleLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : roomEntries.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          신청한 과목의 건물 정보가 없어 강의실 안내를 제공할 수 없습니다.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {roomEntries.map((e) => {
            const key = `${e.building}-${e.room}`;
            return (
              <button
                key={key}
                onClick={() => setManualKey(key)}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-sm",
                  key === selectedKey
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:text-foreground"
                )}
              >
                {e.name} · {dayLabel[e.day]} {e.startTime}
              </button>
            );
          })}
        </div>
      )}

      {selectedKey && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {roomLoading || !room ? (
                <Skeleton className="h-5 w-32" />
              ) : (
                `${room.building} ${room.floor}층 ${room.room}호`
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {roomLoading || !room ? (
              <Skeleton className="h-24 w-full" />
            ) : (
              <ol className="space-y-2">
                {room.directions.map((step, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Badge variant="outline" className="mt-0.5 h-5 w-5 justify-center p-0">
                      {i + 1}
                    </Badge>
                    {step}
                  </li>
                ))}
              </ol>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
