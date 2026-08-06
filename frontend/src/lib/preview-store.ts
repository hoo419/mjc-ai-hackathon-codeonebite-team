// 실제 수강신청 API와 무관한, 화면 전용 "시간표 미리보기" 상태.
// 학생이 실제로 신청하지 않고 시간표에 넣어보는 용도.
let previewIds: string[] = [];
const listeners = new Set<() => void>();

export function getPreviewIds() {
  return previewIds;
}

export function togglePreview(courseId: string) {
  previewIds = previewIds.includes(courseId)
    ? previewIds.filter((id) => id !== courseId)
    : [...previewIds, courseId];
  listeners.forEach((listener) => listener());
}

export function subscribePreview(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
