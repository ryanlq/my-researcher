"use client";

import { useState } from "react";
import {
    PromptInput,
    PromptInputActions,
    PromptInputAction,
    PromptInputTextarea,
} from "@/components/ui/prompt-input";
import { Button } from "@/components/ui/button";
import { Send, Loader2 } from "lucide-react";
import { useResearchStore } from "@/stores/research";
import { ReportType, ReportSource } from "@/types/research";
import { SourceSelector } from "@/components/research/SourceSelector";
import { UrlInputList } from "@/components/research/UrlInputList";
import { DocumentSelector } from "@/components/research/DocumentSelector";

export function ResearchPromptInput() {
    const [query, setQuery] = useState("");
    const [reportType, setReportType] = useState<ReportType>("research_report");
    const [language, setLanguage] = useState("chinese");
    const [reportSource, setReportSource] = useState<ReportSource>("web");
    const [sourceUrls, setSourceUrls] = useState<string[]>([]);
    const [complementSourceUrls, setComplementSourceUrls] = useState(false);
    const [documentIds, setDocumentIds] = useState<string[]>([]);
    const { setCurrentResearch, setViewState, isLoading } = useResearchStore();

    const handleSubmit = () => {
        if (!query.trim() || isLoading) return;

        // 验证指定来源研究必须提供URL
        if (reportSource === "static" && sourceUrls.length === 0) {
            alert("请至少添加一个URL");
            return;
        }

        // 验证本地文档研究必须选择文档
        if (reportSource === "local" && documentIds.length === 0) {
            alert("请至少选择一个文档");
            return;
        }

        // 验证混合研究必须有URL或文档
        if (
            reportSource === "hybrid" &&
            sourceUrls.length === 0 &&
            documentIds.length === 0
        ) {
            alert("请至少添加一个URL或选择一个文档");
            return;
        }

        console.log("📝 创建新研究:", {
            query,
            reportType,
            reportSource,
            sourceUrls,
            documentIds,
        });

        // 设置当前研究
        setCurrentResearch({
            query,
            report_type: reportType,
            status: "running",
            report: null,
            sources: [],
            costs: 0,
            images: [],
            report_source: reportSource,
            source_urls: sourceUrls,
            complement_source_urls: complementSourceUrls,
            document_ids: documentIds,
        });

        // 验证是否设置成功
        setTimeout(() => {
            const store = useResearchStore.getState();
            console.log("✅ currentResearch 已设置:", store.currentResearch);
        }, 100);

        // 切换到进度视图
        setViewState("progress");
    };

    return (
        <div className="w-full max-w-4xl mx-auto px-4">
            <div className="space-y-6">
                {/* 研究来源选择器 */}
                <div className="bg-card rounded-lg border p-4">
                    <SourceSelector
                        value={reportSource}
                        onChange={setReportSource}
                        disabled={isLoading}
                    />
                </div>

                {/* URL输入列表 - 仅在static模式显示 */}
                {reportSource === "static" && (
                    <div className="bg-card rounded-lg border p-4">
                        <UrlInputList
                            urls={sourceUrls}
                            onChange={setSourceUrls}
                            complementSourceUrls={complementSourceUrls}
                            onComplementChange={setComplementSourceUrls}
                            disabled={isLoading}
                        />
                    </div>
                )}

                {/* 文档选择器 - 仅在local模式显示 */}
                {reportSource === "local" && (
                    <div className="bg-card rounded-lg border p-4">
                        <DocumentSelector
                            selectedIds={documentIds}
                            onChange={setDocumentIds}
                            disabled={isLoading}
                        />
                    </div>
                )}

                {/* 混合模式 - URL + 文档 */}
                {reportSource === "hybrid" && (
                    <div className="space-y-4">
                        <div className="bg-card rounded-lg border p-4">
                            <UrlInputList
                                urls={sourceUrls}
                                onChange={setSourceUrls}
                                complementSourceUrls={complementSourceUrls}
                                onComplementChange={setComplementSourceUrls}
                                disabled={isLoading}
                            />
                        </div>
                        <div className="bg-card rounded-lg border p-4">
                            <DocumentSelector
                                selectedIds={documentIds}
                                onChange={setDocumentIds}
                                disabled={isLoading}
                            />
                        </div>
                    </div>
                )}

                {/* 主题输入 */}
                <PromptInput
                    value={query}
                    onValueChange={setQuery}
                    onSubmit={handleSubmit}
                    className="shadow-lg"
                    disabled={isLoading}
                >
                    <PromptInputTextarea
                        placeholder="输入你想研究的主题...（例如：2025年人工智能在医疗领域的最新应用）"
                        className="min-h-[120px] text-base"
                    />

                    <PromptInputActions className="bg-background p-2">
                        {/* 模式选择 */}
                        <select
                            value={reportType}
                            onChange={(e) =>
                                setReportType(e.target.value as ReportType)
                            }
                            className="h-9 rounded-md border bg-background px-3 py-1 text-sm"
                            disabled={isLoading}
                        >
                            <option value="research_report">
                                快速研究 (1-2分钟)
                            </option>
                            <option value="deep">深度研究 (5-10分钟)</option>
                            <option value="multi_agent">
                                多智能体协作 (10-20分钟)
                            </option>
                        </select>

                        {/* 语言选择 */}
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="h-9 rounded-md border bg-background px-3 py-1 text-sm"
                            disabled={isLoading}
                        >
                            <option value="chinese">中文</option>
                            <option value="english">English</option>
                        </select>

                        <div className="flex-1" />

                        {/* 发送按钮 */}
                        <Button
                            size="icon"
                            onClick={handleSubmit}
                            disabled={
                                !query.trim() ||
                                isLoading ||
                                (reportSource === "static" &&
                                    sourceUrls.length === 0) ||
                                (reportSource === "local" &&
                                    documentIds.length === 0) ||
                                (reportSource === "hybrid" &&
                                    sourceUrls.length === 0 &&
                                    documentIds.length === 0)
                            }
                        >
                            {isLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Send className="h-4 w-4" />
                            )}
                        </Button>
                    </PromptInputActions>
                </PromptInput>

                <div className="text-center text-sm text-muted-foreground">
                    按 <kbd className="px-1 py-0.5 rounded bg-muted">Enter</kbd>{" "}
                    开始研究，
                    <kbd className="px-1 py-0.5 rounded bg-muted ml-1">
                        Shift + Enter
                    </kbd>{" "}
                    换行
                </div>
            </div>
        </div>
    );
}
