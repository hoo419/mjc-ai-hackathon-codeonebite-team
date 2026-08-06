import type { LucideIcon } from "lucide-react";
import { CalendarDays, DoorOpen, Home, MessageCircle, Search, Users } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const navItems: NavItem[] = [
  { href: "/", label: "대시보드", icon: Home },
  { href: "/chat", label: "AI 비서", icon: MessageCircle },
  { href: "/courses", label: "과목검색", icon: Search },
  { href: "/schedule", label: "시간표", icon: CalendarDays },
  { href: "/rooms", label: "강의실", icon: DoorOpen },
  { href: "/counseling", label: "상담", icon: Users },
];
