import buildingsData from "@/mocks/buildings.json";
import roomsData from "@/mocks/rooms.json";
import type { Building, Room } from "@/types";

// GET /buildings
export async function getBuildings(): Promise<{ buildings: Building[] }> {
  return { buildings: buildingsData as Building[] };
}

// GET /rooms/{roomId}
export async function getRoom(roomId: string): Promise<{ room: Room | null }> {
  const room = (roomsData as Room[]).find((r) => r.id === roomId) ?? null;
  return { room };
}

export function roomIdFor(building: string | null, room: string | null): string | null {
  if (!building || !room) return null;
  const buildingEntry = (buildingsData as Building[]).find((b) => b.name === building);
  if (!buildingEntry) return null;
  return `${buildingEntry.id}-${room}`;
}
