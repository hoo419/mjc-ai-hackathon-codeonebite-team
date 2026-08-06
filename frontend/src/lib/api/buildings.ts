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

// data/rooms.json의 id는 강의실 원본 코드(예: "공502") 자체다 - 건물명을 몰라도
// room 코드만으로 고유하게 식별되므로 별도 매핑 없이 그대로 쓴다.
export function roomIdFor(room: string | null): string | null {
  return room && room.trim() ? room.trim() : null;
}
