import type { Day } from "@/types";

export const DAY_ORDER: Day[] = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];

export function toMinutes(time: string): number {
  const [h, m] = time.split(":").map(Number);
  return h * 60 + m;
}

export function todayAsDay(date = new Date()): Day {
  const jsDay = date.getDay(); // 0=Sun..6=Sat
  return DAY_ORDER[(jsDay + 6) % 7];
}

export function nowMinutes(date = new Date()): number {
  return date.getHours() * 60 + date.getMinutes();
}
