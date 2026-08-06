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

// building은 항상 null이다(원본이 "공502" 같은 축약 코드뿐이라 정식 건물명을
// 지어내지 않기로 함). data/rooms.json의 id는 이 축약 코드(예: "공502") 자체를
// 그대로 쓰므로, room 코드만으로 고유하게 강의실을 식별/조회할 수 있다.
function uniqueRoomEntries(schedule: ScheduleEntry[]): ScheduleEntry[] {
  const seen = new Set<string>();
  return schedule.filter((e) => {
    if (!e.room) return false;
    if (seen.has(e.room)) return false;
    seen.add(e.room);
    return true;
  });
}

export default function RoomsPage() {
  const { data: scheduleData, loading: scheduleLoading } = useAsyncData(() => getMySchedule());
  const schedule = scheduleData?.schedule ?? [];
  const roomEntries = uniqueRoomEntries(schedule);
  const nextClass = getNextClass(schedule);

  const [manualKey, setManualKey] = useState<string | null>(null);
  const defaultKey = nextClass?.room ?? null;
  const selectedKey = manualKey ?? defaultKey;

  const selectedEntry = roomEntries.find((e) => e.room === selectedKey) ?? null;
  const selectedRoomId = roomIdFor(selectedEntry?.room ?? null);

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
          {roomEntries.map((e) => (
            <button
              key={e.room}
              onClick={() => setManualKey(e.room)}
              className={cn(
                "rounded-full border px-3 py-1.5 text-sm",
                e.room === selectedKey
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:text-foreground"
              )}
            >
              {e.name} · {dayLabel[e.day]} {e.startTime}
            </button>
          ))}
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
