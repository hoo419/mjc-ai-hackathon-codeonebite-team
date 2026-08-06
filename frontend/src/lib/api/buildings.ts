import buildingsData from "@/mocks/buildings.json";
import type { Building, Room } from "@/types";
import { apiGet } from "./client";

// GET /buildings
export function getBuildings(): Promise<{ buildings: Building[] }> {
  return apiGet<{ buildings: Building[] }>("/buildings");
}

// GET /rooms/{roomId}
export async function getRoom(roomId: string): Promise<{ room: Room | null }> {
  try {
    return await apiGet<{ room: Room }>(`/rooms/${roomId}`);
  } catch {
    return { room: null };
  }
}

// roomIdFor는 building 이름 -> buildings.json의 id 매핑이 필요해 Mock 목록을
// 그대로 참조한다 (백엔드 GET /buildings 응답과 data/buildings.json이 동일한
// id 체계를 쓰므로 안전하다).
export function roomIdFor(building: string | null, room: string | null): string | null {
  if (!building || !room) return null;
  const buildingEntry = (buildingsData as Building[]).find((b) => b.name === building);
  if (!buildingEntry) return null;
  return `${buildingEntry.id}-${room}`;
}
