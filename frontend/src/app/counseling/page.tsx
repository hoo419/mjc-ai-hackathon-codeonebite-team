"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useAsyncData } from "@/hooks/use-async-data";
import { analyzeAptitude, getMyCounseling, requestCounseling } from "@/lib/api";
import { ApiError } from "@/lib/api/client";
import { formatDateTime } from "@/lib/time";
import type { AptitudeAnalysisResult, CounselingTargetType } from "@/types";

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

  const [rawText, setRawText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AptitudeAnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  async function handleRequest(type: CounselingTargetType) {
    setRequestingType(type);
    setResult(null);
    const res = await requestCounseling(type, message || "상담을 요청합니다.");
    setResult(`요청이 접수되었습니다 (${res.requestId})`);
    setRequestingType(null);
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalysisError(null);
    setAnalysis(null);
    try {
      const res = await analyzeAptitude(rawText);
      setAnalysis(res);
    } catch (e) {
      setAnalysisError(e instanceof ApiError ? e.message : "분석하지 못했습니다.");
    } finally {
      setAnalyzing(false);
    }
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
          <CardTitle className="text-sm">진로적성검사 결과 AI 분석</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-xs text-muted-foreground">
            <a
              href="https://mpu.mjc.ac.kr/"
              target="_blank"
              rel="noreferrer"
              className="underline underline-offset-2 hover:text-foreground"
            >
              학생역량 이력관리 시스템(SMART CARE)
            </a>
            에 직접 로그인해서 진로적성검사 · 핵심역량검사 · 종합심리검사 결과를 확인한
            뒤, 그 내용을 복사해서 아래에 붙여넣어 주세요. 로그인 아이디/비밀번호는
            여기서 입력하지 않습니다.
          </p>
          <Textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder="mpu.mjc.ac.kr에서 복사한 검사 결과를 붙여넣으세요"
          />
          <Button onClick={handleAnalyze} disabled={analyzing || !rawText.trim()}>
            {analyzing ? "분석 중..." : "AI로 분석하기"}
          </Button>
          {analysisError && <p className="text-sm text-destructive">{analysisError}</p>}
          {analysis && (
            <div className="space-y-2 rounded-lg border p-3 text-sm">
              <p>{analysis.summary}</p>
              {analysis.insights.length > 0 && (
                <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                  {analysis.insights.map((insight, i) => (
                    <li key={i}>{insight}</li>
                  ))}
                </ul>
              )}
            </div>
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
