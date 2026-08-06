"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { updateMe } from "@/lib/api";
import type { Student } from "@/types";
import { Pencil } from "lucide-react";

// 학교 포털(SSO) 로그인은 학생이 직접 하고, 거기서 확인한 학과/학년/학기를
// 이 폼에 입력한다. 이 앱은 학교 로그인 아이디/비밀번호를 절대 다루지 않는다.
export function ProfileEditDialog({
  student,
  onUpdated,
}: {
  student: Student;
  onUpdated: (student: Student) => void;
}) {
  const [open, setOpen] = useState(false);
  const [department, setDepartment] = useState(student.department);
  const [grade, setGrade] = useState(String(student.grade));
  const [semester, setSemester] = useState(String(student.semester));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const { student: updated } = await updateMe({
        department,
        grade: Number(grade),
        semester: Number(semester),
      });
      onUpdated(updated);
      setOpen(false);
    } catch {
      setError("저장하지 못했습니다. 다시 시도해 주세요.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="ghost" size="icon-sm" />}>
        <Pencil className="h-3.5 w-3.5" />
        <span className="sr-only">학과/학년/학기 수정</span>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>학과/학년/학기 수정</DialogTitle>
          <DialogDescription>
            학교 포털에 직접 로그인해서 확인한 정보를 입력해 주세요. 아이디/비밀번호는
            여기서 입력하지 않습니다.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="department">학과</Label>
            <Input
              id="department"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            />
          </div>
          <div className="flex gap-3">
            <div className="flex flex-1 flex-col gap-1.5">
              <Label htmlFor="grade">학년</Label>
              <Input
                id="grade"
                type="number"
                min={1}
                max={6}
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
              />
            </div>
            <div className="flex flex-1 flex-col gap-1.5">
              <Label htmlFor="semester">학기</Label>
              <Input
                id="semester"
                type="number"
                min={1}
                max={2}
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
              />
            </div>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>
        <DialogFooter>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "저장 중..." : "저장"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
