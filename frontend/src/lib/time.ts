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

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${mm}/${dd} ${hh}:${min}`;
}
