import type { Day, ScheduleEntry } from "@/types";
import { DAY_ORDER, nowMinutes, todayAsDay, toMinutes } from "./time";

export function getTodaySchedule(schedule: ScheduleEntry[], date = new Date()): ScheduleEntry[] {
  const today = todayAsDay(date);
  return schedule
    .filter((e) => e.day === today)
    .sort((a, b) => toMinutes(a.startTime) - toMinutes(b.startTime));
}

export function getNextClass(schedule: ScheduleEntry[], date = new Date()): ScheduleEntry | null {
  const today = todayAsDay(date);
  const now = nowMinutes(date);
  const todayIndex = DAY_ORDER.indexOf(today);

  // offset 7 wraps back to today next week, so a same-day class later
  // this week or next week is never missed.
  for (let offset = 0; offset <= 7; offset++) {
    const day = DAY_ORDER[(todayIndex + offset) % 7];
    const dayEntries = schedule
      .filter((e) => e.day === day)
      .sort((a, b) => toMinutes(a.startTime) - toMinutes(b.startTime));
    const candidates = offset === 0 ? dayEntries.filter((e) => toMinutes(e.startTime) > now) : dayEntries;
    if (candidates.length > 0) return candidates[0];
  }
  return null;
}

interface TimeRange {
  day: Day;
  startTime: string;
  endTime: string;
}

export function hasConflict(a: TimeRange, b: TimeRange): boolean {
  if (a.day !== b.day) return false;
  const aStart = toMinutes(a.startTime);
  const aEnd = toMinutes(a.endTime);
  const bStart = toMinutes(b.startTime);
  const bEnd = toMinutes(b.endTime);
  return aStart < bEnd && bStart < aEnd;
}
