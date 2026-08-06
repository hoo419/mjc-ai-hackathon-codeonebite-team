import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { findDepartmentOffice } from "@/lib/department-offices";
import { MessageCircle, Phone } from "lucide-react";

// 1학년 1학기 학생 전용 안내: 학과 사무실에 연락해서 카카오톡 단톡방에
// 들어가라는 알림. 학과 사무실 전화번호는 각 학과 홈페이지에서 직접 확인한
// 실제 번호(frontend/src/lib/department-offices.ts)만 쓰고, 못 찾은 학과는
// 번호 없이 "학과 사무실에 문의"라는 일반 안내만 보여준다(번호를 지어내지
// 않는다).
export function NewStudentDeptNotice({ department }: { department: string }) {
  const office = findDepartmentOffice(department);

  return (
    <Card className="border-primary/40 bg-primary/5">
      <CardContent className="flex items-start gap-3 py-3 text-sm">
        <MessageCircle className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <div className="flex-1 space-y-1.5">
          <p className="font-medium">1학년 1학기시네요 - 학과 단톡방에 들어가 보세요</p>
          <p className="text-muted-foreground">
            {office?.phone
              ? `${department} 학과 사무실에 연락하면 카카오톡 단체채팅방 초대 링크를 안내받을 수 있습니다.`
              : `${department} 학과 사무실에 문의하면 카카오톡 단체채팅방 초대 링크를 안내받을 수 있습니다 (죄송해요, 이 학과의 정확한 전화번호는 아직 확인하지 못했습니다).`}
          </p>
          {office?.phone && (
            <Button render={<a href={`tel:${office.phone}`} />} variant="secondary" size="sm">
              <Phone className="h-3.5 w-3.5" /> {office.phone}
              {office.office ? ` · ${office.office}` : ""}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
