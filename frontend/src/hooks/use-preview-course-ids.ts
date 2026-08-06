"use client";

import { useSyncExternalStore } from "react";
import { getPreviewIds, subscribePreview } from "@/lib/preview-store";

const EMPTY: string[] = [];

export function usePreviewCourseIds() {
  return useSyncExternalStore(subscribePreview, getPreviewIds, () => EMPTY);
}
