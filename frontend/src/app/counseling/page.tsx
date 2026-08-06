"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useAsyncData } from "@/hooks/use-async-data";
import { analyzeAptitude, getMyCounseling } from "@/lib/api";
import { ApiError } from "@/lib/api/client";
import { formatDateTime } from "@/lib/time";
import type { AptitudeAnalysisResult } from "@/types";
import { Phone } from "lucide-react";

// 명지전문대학교 상담센터 상담지원팀 실제 연락처 (www.mjc.ac.kr 교직원/전화번호
// 검색으로 확인, 2026-08-06 기준). 학과/학년별 지도교수·조교 연락처는 학과마다
// 별도 사이트 구조가 달라 아직 자동 조회를 지원하지 않는다 - 확인 안 된 번호를
// 지어내는 대신, 검증된 상담센터 대표 연락처로 안내한다.
const COUNSELING_CENTER_CONTACTS = [
  { role: "팀장", phone: "02-300-8790" },
  { role: "팀원", phone: "02-300-3751" },
];

export default function CounselingPage() {
  const { data, loading } = useAsyncData(() => getMyCounseling());

  const [rawText, setRawText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AptitudeAnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

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
          <CardTitle className="text-sm">상담 연결</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-xs text-muted-foreground">
            명지전문대학교 상담센터 상담지원팀 연락처입니다 (
            <a
              href="https://www.mjc.ac.kr/"
              target="_blank"
              rel="noreferrer"
              className="underline underline-offset-2 hover:text-foreground"
            >
              www.mjc.ac.kr
            </a>{" "}
            교직원/전화번호 검색으로 확인).
          </p>
          <ul className="space-y-1.5">
            {COUNSELING_CENTER_CONTACTS.map((c) => (
              <li key={c.phone} className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">상담지원팀 {c.role}</span>
                <Button
                  render={<a href={`tel:${c.phone}`} />}
                  variant="secondary"
                  size="sm"
                >
                  <Phone className="h-3.5 w-3.5" /> {c.phone}
                </Button>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
