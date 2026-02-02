"use client";

import { useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useResearchStore } from "@/stores/research";
import { WebSocketClient } from "@/lib/api";
import { Activity, Search, CheckCircle2, XCircle } from "lucide-react";

interface ResearchProgressProps {
  researchId: number;
}

export default function ResearchProgress({ researchId }: ResearchProgressProps) {
  const { progress, currentResearch, updateResearch, setProgress } = useResearchStore();
  const wsClientRef = useRef<WebSocketClient | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // 如果已经有连接，不要重复连接
    if (wsClientRef.current) {
      return;
    }

    // 延迟连接，避免 React Strict Mode 导致的立即 unmount
    timeoutRef.current = setTimeout(() => {
      const client = new WebSocketClient(researchId.toString());

      client.connect(
        (data) => {
          console.log("📨 WebSocket message:", data);

          if (data.event === "research.progress") {
            setProgress(data);
            updateResearch(researchId, {
              status: data.status,
              progress_percentage: data.progress_percentage,
              completed_queries: data.completed_queries,
              total_queries: data.total_queries,
            });
          } else if (data.event === "research.completed") {
            setProgress(null);
            updateResearch(researchId, {
              status: "completed",
              progress_percentage: 100,
            });
          } else if (data.event === "research.error") {
            setProgress(null);
            updateResearch(researchId, {
              status: "failed",
            });
          }
        },
        (error) => {
          // 静默处理错误，不打印到控制台
        },
        () => {
          console.log("🔌 WebSocket connection closed");
        }
      );

      wsClientRef.current = client;
    }, 100); // 延迟 100ms 连接

    // 清理函数
    return () => {
      // 清除延迟定时器
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      // 断开 WebSocket
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
        wsClientRef.current = null;
      }
    };
  }, [researchId]); // 只依赖 researchId

  // 如果没有进度且当前研究不存在，不显示
  if (!progress && !currentResearch) return null;

  const status = progress?.status || currentResearch?.status || "pending";
  const percentage = progress?.progress_percentage || currentResearch?.progress_percentage || 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {status === "completed" && <CheckCircle2 className="h-5 w-5 text-green-500" />}
            {status === "failed" && <XCircle className="h-5 w-5 text-red-500" />}
            {status === "running" && <Activity className="h-5 w-5 animate-pulse text-blue-500" />}
            {status === "pending" && <Search className="h-5 w-5 text-muted-foreground" />}
            研究进度
          </CardTitle>
          <span className="text-sm text-muted-foreground">
            {percentage.toFixed(0)}%
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={percentage} />

        {progress && (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-muted-foreground">
              <span>当前查询:</span>
              <span className="text-foreground font-medium truncate ml-2 max-w-[300px]">
                {progress.current_query || "准备中..."}
              </span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>已完成查询:</span>
              <span className="text-foreground font-medium">
                {progress.completed_queries} / {progress.total_queries}
              </span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>研究深度:</span>
              <span className="text-foreground font-medium">
                第 {progress.current_depth} 层 / 共 {progress.total_depth} 层
              </span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>当前花费:</span>
              <span className="text-foreground font-medium">
                ${progress.cost.toFixed(4)}
              </span>
            </div>
          </div>
        )}

        {status === "completed" && (
          <div className="p-4 bg-green-50 dark:bg-green-950 rounded-md border border-green-200 dark:border-green-900">
            <p className="text-sm font-medium text-green-900 dark:text-green-100">
              ✓ 研究已完成！
            </p>
          </div>
        )}

        {status === "failed" && (
          <div className="p-4 bg-red-50 dark:bg-red-950 rounded-md border border-red-200 dark:border-red-900">
            <p className="text-sm font-medium text-red-900 dark:text-red-100">
              ✗ 研究失败，请重试
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
