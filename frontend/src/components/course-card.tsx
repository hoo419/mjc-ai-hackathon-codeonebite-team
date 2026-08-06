import { Badge } from "@/components/ui/badge";
import { Card, CardAction, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { categoryLabel, classTypeLabel, dayLabel, statusBadgeVariant, statusLabel } from "@/lib/labels";
import { formatDateTime } from "@/lib/time";
import type { Course } from "@/types";
import type { ReactNode } from "react";

export function CourseCard({ course, footer }: { course: Course; footer?: ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{course.name}</CardTitle>
        <p className="text-xs text-muted-foreground">
          {course.professor} · {course.credits}학점 · {categoryLabel[course.category]}
        </p>
        <CardAction>
          <Badge variant={statusBadgeVariant[course.status]}>{statusLabel[course.status]}</Badge>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-1 text-sm">
        <p>
          {dayLabel[course.day]} {course.startTime}~{course.endTime} · {classTypeLabel[course.classType]}
        </p>
        <p className="text-muted-foreground">
          {course.building ? `${course.building} ${course.room}호` : "온라인 (장소 없음)"}
        </p>
        <p className="text-muted-foreground">
          {course.enrolled}/{course.capacity}명 · 갱신 {formatDateTime(course.lastUpdated)}
        </p>
      </CardContent>
      {footer && <CardFooter className="gap-2">{footer}</CardFooter>}
    </Card>
  );
}
