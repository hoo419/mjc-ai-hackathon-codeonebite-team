"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useAsyncData } from "@/hooks/use-async-data";
import { getMyCounseling, requestCounseling } from "@/lib/api";
import { formatDateTime } from "@/lib/time";
import type { CounselingTargetType } from "@/types";

const TARGETS: { type: CounselingTargetType; label: string }[] = [
  { type: "ADVISOR", label: "지도교수 연결" },
  { type: "CAREER_COUNSELOR", label: "진로상담사 연결" },
  { type: "DEPARTMENT_OFFICE", label: "학과사무실 문의" },
];

export default function CounselingPage() {
  const { data, loading } = useAsyncData(() => getMyCounseling());
  const [message, setMessage] = useState("");
  const [requestingType, setRequestingType] = useState<CounselingTargetType | null>(null);
  const [result, setResult] = useState<string | null>(null);

  async function handleRequest(type: CounselingTargetType) {
    setRequestingType(type);
    setResult(null);
    const res = await requestCounseling(type, message || "상담을 요청합니다.");
    setResult(`요청이 접수되었습니다 (${res.requestId})`);
    setRequestingType(null);
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-4">
      <h1 className="font-heading text-lg font-semibold">상담</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">진로·검사 결과 요약</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {loading || !data ? (
            <>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </>
          ) : (
            <>
              <p>{data.careerSummary}</p>
              <p className="text-muted-foreground">{data.personalitySummary}</p>
              <p className="text-xs text-muted-foreground">
                최근 상담일: {formatDateTime(data.lastCounselingAt)}
              </p>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">상담 요청</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="상담 요청 메시지 (선택)"
          />
          <div className="flex flex-col gap-2 sm:flex-row">
            {TARGETS.map((t) => (
              <Button
                key={t.type}
                variant="secondary"
                className="flex-1"
                disabled={requestingType === t.type}
                onClick={() => handleRequest(t.type)}
              >
                {t.label}
              </Button>
            ))}
          </div>
          {result && <p className="text-sm text-foreground">{result}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
