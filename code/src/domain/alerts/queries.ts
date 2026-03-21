import { useQuery } from "@tanstack/react-query";
import { http } from "@/api/http/client";
import type { Alert } from "./types";

export function useAlerts() {
  return useQuery<Alert[]>({
    queryKey: ["alerts"],
    queryFn: async () => {
      const res = await http.get<Alert[]>("/alerts");
      return res.data;
    },
    refetchInterval: 10_000,
  });
}
