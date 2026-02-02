"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Markdown } from "@/components/ui/markdown";
import { Loader, CircularLoader } from "@/components/ui/loader";
import {
    CheckCircle2,
    Circle,
    FileText,
    Globe,
    Image as ImageIcon,
    ChevronDown,
    Download,
} from "lucide-react";

// 研究步骤定义
const RESEARCH_STEPS = [
    { id: "plan", label: "规划研究策略", icon: "📋" },
    { id: "search", label: "搜索相关信息", icon: "🔍" },
    { id: "scrape", label: "抓取网页内容", icon: "🌐" },
    { id: "analyze", label: "分析数据", icon: "🧠" },
    { id: "report", label: "生成报告", icon: "✍️" },
];

interface ResearchProgressPromptKitProps {
    query: string;
    reportType?: string;
    reportSource?: string;
    sourceUrls?: string[];
    complementSourceUrls?: boolean;
    documentIds?: string[];
    onStart?: () => void;
    onComplete?: (data: { report: string; sources: Source[]; images: Image[]; costs: number }) => void;
    onError?: (error: string) => void;
}

interface LogEntry {
    id: string;
    type: string;
    output: string;
    timestamp: number;
}

interface Source {
    url: string;
    title?: string;
}

interface Image {
    url: string;
    description?: string;
}

export default function ResearchProgressPromptKit({
    query,
    reportType = "research_report",
    reportSource = "web",
    sourceUrls = [],
    complementSourceUrls = false,
    documentIds = [],
    onStart,
    onComplete,
    onError,
}: ResearchProgressPromptKitProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [sources, setSources] = useState<Source[]>([]);
    const [images, setImages] = useState<Image[]>([]);
    const [report, setReport] = useState("");
    const [costs, setCosts] = useState(0);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isCompleted, setIsCompleted] = useState(false); // 新增：标记是否已完成

    // Collapsible 状态：当报告生成完成时自动折叠
    const [isProgressOpen, setIsProgressOpen] = useState(true);
    const isReportComplete = isCompleted && report; // 修改：使用 isCompleted 状态

    const wsRef = useRef<WebSocket | null>(null);
    const reportEndRef = useRef<HTMLDivElement>(null);
    const completedRef = useRef(false); // 新增：用 ref 跟踪完成状态，避免闭包问题
    const callbacksRef = useRef({ onStart, onComplete, onError });

    // 当报告完成时自动折叠进度部分
    useEffect(() => {
        if (isReportComplete) {
            setIsProgressOpen(false);
        }
    }, [isReportComplete]);

    // 监听完成状态（仅用于自动折叠进度部分）
    useEffect(() => {
        if (isCompleted && report) {
            console.log("✅ 研究完成，折叠进度部分");
        }
    }, [isCompleted, report]);

    // 更新回调引用
    useEffect(() => {
        callbacksRef.current = { onStart, onComplete, onError };
    }, [onStart, onComplete, onError]);

    // 自动滚动到报告底部
    useEffect(() => {
        if (reportEndRef.current) {
            reportEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [report]);

    // 下载报告为 Markdown 文件
    const handleDownload = () => {
        if (!report) return;

        // 创建文件内容（包含元数据）
        const content = `# ${query}

**生成时间:** ${new Date().toLocaleString('zh-CN')}
**来源数量:** ${sources.length}
**成本:** $${costs.toFixed(4)}
**报告类型:** ${reportType === "research_report" ? "快速研究" : reportType === "deep" ? "深度研究" : "多智能体"}

---

## 参考来源

${sources.map((source, index) => `${index + 1}. ${source.url}`).join('\n')}

${images.length > 0 ? `
## 相关图片

${images.map((image, index) => `${index + 1}. ${image.url}${image.description ? ` (${image.description})` : ''}`).join('\n')}
` : ''}

---

## 研究报告

${report}
`;

        // 创建 Blob 并下载
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${query.slice(0, 50)}.md`; // 文件名使用前50个字符
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    // 组件挂载时自动开始研究
    useEffect(() => {
        if (wsRef.current || !query.trim()) {
            console.log("⏭️ 跳过 WebSocket 连接:", {
                hasWs: !!wsRef.current,
                hasQuery: !!query.trim(),
            });
            return;
        }

        callbacksRef.current.onStart?.();

        console.log("🚀 开始 WebSocket 连接...");

        // 重置状态
        setCurrentStep(0);
        setLogs([]);
        setSources([]);
        setImages([]);
        setReport("");
        setCosts(0);
        setError(null);
        setIsCompleted(false); // 重置完成状态
        completedRef.current = false; // 重置完成 ref
        setIsProgressOpen(true); // 开始新研究时展开进度部分

        // 建立 WebSocket 连接
        const wsUrl = `ws://localhost:8000/ws/research`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("✅ WebSocket 连接成功，发送研究请求...");

            // 构建请求数据
            const requestData: any = {
                query: query,
                report_type: reportType,
                report_format: "markdown",
                tone: "objective",
                report_source: reportSource,
            };

            // 如果有指定URL，添加到请求中
            if (sourceUrls && sourceUrls.length > 0) {
                requestData.source_urls = sourceUrls;
                requestData.complement_source_urls = complementSourceUrls;
            }

            // ✨ 如果有文档ID，添加到请求中
            if (documentIds && documentIds.length > 0) {
                requestData.document_ids = documentIds;
            }

            ws.send(JSON.stringify(requestData));
            console.log("📤 发送的请求数据:", requestData);

            setIsConnected(true);

            // 注意：不需要手动发送心跳
            // Uvicorn 会在协议层自动处理 WebSocket ping/pong
        };

        ws.onmessage = (event) => {
            try {
                const data: LogEntry = JSON.parse(event.data);
                processLog(data);
            } catch (err) {
                console.error("Failed to parse WebSocket message:", err);
            }
        };

        ws.onerror = (event) => {
            console.error("❌ WebSocket error:", event);
            const errorMsg = "连接服务器失败，请检查后端是否运行";
            setError(errorMsg);
            callbacksRef.current.onError?.(errorMsg);
        };

        ws.onclose = (event) => {
            console.log("🔌 WebSocket 连接关闭", event.code, event.reason);
            setIsConnected(false);
            wsRef.current = null;

            // 兼容：如果没有收到 completed 事件但在正常关闭时有报告，标记为完成
            // useEffect 会检测到 isCompleted 变化并触发回调
            if (!completedRef.current && report && event.code === 1000) {
                console.log("📝 WebSocket 正常关闭，标记为完成");
                setIsCompleted(true);
            }
        };

        wsRef.current = ws;

        return () => {
            console.log("🧹 准备清理 WebSocket 连接，状态:", ws.readyState);

            if (ws.readyState === WebSocket.OPEN) {
                console.log("🧹 关闭 WebSocket 连接");
                ws.close();
                wsRef.current = null;
            } else if (ws.readyState === WebSocket.CONNECTING) {
                console.log("⚠️ WebSocket 正在连接中，不关闭（避免连接失败）");
            } else {
                console.log("ℹ️ WebSocket 未连接，无需关闭");
                wsRef.current = null;
            }
        };
    }, []);

    // 处理日志消息
    const processLog = (log: LogEntry) => {
        if (log.type !== "report") {
            setLogs((prev) => [...prev, log]);
        }

        switch (log.type) {
            case "plan":
                setCurrentStep(0);
                break;

            case "search":
                setCurrentStep(1);
                break;

            case "scrape":
                setCurrentStep(2);
                break;

            case "analyze":
                setCurrentStep(3);
                break;

            case "report":
                setCurrentStep(4);
                if (log.output && typeof log.output === "string") {
                    setReport((prev) => prev + log.output);
                }
                break;

            case "source":
                if (log.output && typeof log.output === "string") {
                    try {
                        const sourceData = JSON.parse(log.output);
                        setSources((prev) => [
                            ...prev,
                            {
                                url: sourceData.url || log.output,
                                title: sourceData.title,
                            },
                        ]);
                    } catch {
                        setSources((prev) => [...prev, { url: log.output }]);
                    }
                }
                break;

            case "image":
                if (log.output && typeof log.output === "string") {
                    try {
                        const imageData = JSON.parse(log.output);
                        setImages((prev) => [
                            ...prev,
                            {
                                url: imageData.url || log.output,
                                description: imageData.description,
                            },
                        ]);
                    } catch {
                        setImages((prev) => [...prev, { url: log.output }]);
                    }
                }
                break;

            case "completed":
                // 处理完成事件，包含最终数据
                console.log("✅ 收到完成事件:", log);

                // 确保在最后一步
                setCurrentStep(4);

                // 准备最终数据（直接从 log 中提取，不依赖状态）
                const finalReport = log.report || "";
                const finalSources = log.sources && Array.isArray(log.sources)
                    ? log.sources.map((s: any) => typeof s === "string" ? s : s.url)
                    : [];
                const finalImages = log.images && Array.isArray(log.images)
                    ? log.images.map((img: any) => typeof img === "string" ? img : img.url)
                    : [];
                const finalCosts = typeof log.costs === "number" ? log.costs : 0;

                console.log("📝 准备调用完成回调", {
                    reportLength: finalReport.length,
                    sourcesCount: finalSources.length,
                    imagesCount: finalImages.length,
                    costs: finalCosts,
                });

                // 同步调用回调，使用 log 中的数据（不依赖状态）
                callbacksRef.current.onComplete?.({
                    report: finalReport,
                    sources: finalSources,
                    images: finalImages,
                    costs: finalCosts,
                });

                // 然后更新状态（异步，不影响回调）
                setReport(finalReport);
                setSources(finalSources.map(s => ({ url: s })));
                setImages(finalImages.map(img => ({ url: img })));
                setCosts(finalCosts);
                setIsCompleted(true);
                completedRef.current = true;
                break;

            default:
                break;
        }
    };

    // 渲染步骤
    const renderStep = (step: (typeof RESEARCH_STEPS)[0], index: number) => {
        const stepIsCompleted = index < currentStep || (isCompleted && index === currentStep);
        const stepIsCurrent = index === currentStep && !isCompleted;

        return (
            <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                    {stepIsCompleted ? (
                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                    ) : stepIsCurrent ? (
                        <CircularLoader size="md" className="!border-blue-500" />
                    ) : (
                        <Circle className="w-5 h-5 text-gray-300 dark:text-gray-600" />
                    )}
                </div>
                <div
                    className={`text-sm ${stepIsCurrent ? "font-semibold text-blue-600 dark:text-blue-400" : "text-gray-600 dark:text-gray-400"}`}
                >
                    {step.icon} {step.label}
                </div>
            </div>
        );
    };

    return (
        <div className="w-full space-y-6">
            {/* 错误提示 */}
            {error && (
                <Card className="border-red-500 bg-red-50 dark:bg-red-900/20">
                    <CardContent className="pt-6">
                        <p className="text-red-600 dark:text-red-400">
                            {error}
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* 进度控制和详情（可折叠） */}
            <Collapsible open={isProgressOpen} onOpenChange={setIsProgressOpen}>
                <CollapsibleTrigger asChild>
                    <Card className="cursor-pointer hover:shadow-md transition-shadow">
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <FileText className="w-5 h-5" />
                                    <span className="font-semibold">
                                        {isReportComplete
                                            ? "研究进度和详情（已折叠）"
                                            : "研究进度和详情"}
                                    </span>
                                    {isConnected && !isReportComplete && (
                                        <Loader variant="dots" size="sm" />
                                    )}
                                </div>
                                <ChevronDown
                                    className={`w-5 h-5 transition-transform ${
                                        isProgressOpen
                                            ? "transform rotate-180"
                                            : ""
                                    }`}
                                />
                            </div>
                        </CardContent>
                    </Card>
                </CollapsibleTrigger>

                <CollapsibleContent className="space-y-6">
                    {/* 研究步骤 */}
                    <Card>
                        <CardHeader>
                            <CardTitle>研究步骤</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {RESEARCH_STEPS.map((step, index) => (
                                    <div key={step.id}>
                                        {renderStep(step, index)}
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* 可折叠的详细信息 */}
                    <Card>
                        <CardContent className="pt-6">
                            <Accordion
                                type="multiple"
                                defaultValue={["logs"]}
                                className="w-full"
                            >
                                {/* 研究日志（可折叠） */}
                                <AccordionItem
                                    value="logs"
                                    className="border-b"
                                >
                                    <AccordionTrigger className="hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <FileText className="w-4 h-4" />
                                            <span>
                                                研究日志 ({logs.length})
                                            </span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent>
                                        <div className="space-y-2 max-h-96 overflow-y-auto">
                                            {logs.length === 0 ? (
                                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                                    等待日志...
                                                </p>
                                            ) : (
                                                logs.map((log, index) => (
                                                    <div
                                                        key={
                                                            log.id ||
                                                            `log-${index}-${log.type}`
                                                        }
                                                        className="text-sm p-2 bg-gray-50 dark:bg-gray-800 rounded"
                                                    >
                                                        <span className="text-gray-500 dark:text-gray-400 text-xs">
                                                            [
                                                            {log.timestamp
                                                                ? new Date(
                                                                      log.timestamp,
                                                                  ).toLocaleTimeString()
                                                                : new Date().toLocaleTimeString()}
                                                            ]
                                                        </span>
                                                        <span className="ml-2">
                                                            {log.output}
                                                        </span>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* 参考来源（可折叠） */}
                                <AccordionItem
                                    value="sources"
                                    className="border-b"
                                >
                                    <AccordionTrigger className="hover:no-underline">
                                        <div className="flex items-center gap-2">
                                            <Globe className="w-4 h-4" />
                                            <span>
                                                参考来源 ({sources.length})
                                            </span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent>
                                        <div className="flex flex-wrap gap-2 max-h-96 overflow-y-auto">
                                            {sources.length === 0 ? (
                                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                                    等待来源...
                                                </p>
                                            ) : (
                                                sources.map((source, index) => (
                                                    <Badge
                                                        key={`source-${source.url}-${index}`}
                                                        variant="outline"
                                                        className="text-xs"
                                                    >
                                                        <a
                                                            href={source.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="hover:underline"
                                                        >
                                                            {source.title ||
                                                                new URL(
                                                                    source.url,
                                                                ).hostname}
                                                        </a>
                                                    </Badge>
                                                ))
                                            )}
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>

                                {/* 选择的图片（可折叠） */}
                                {images.length > 0 && (
                                    <AccordionItem value="images">
                                        <AccordionTrigger className="hover:no-underline">
                                            <div className="flex items-center gap-2">
                                                <ImageIcon className="w-4 h-4" />
                                                <span>
                                                    选择的图片 ({images.length})
                                                </span>
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <div className="grid grid-cols-3 gap-2 max-h-96 overflow-y-auto">
                                                {images.map((image, index) => (
                                                    <a
                                                        key={`image-${image.url}-${index}`}
                                                        href={image.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="aspect-video bg-gray-100 dark:bg-gray-800 rounded overflow-hidden"
                                                    >
                                                        <img
                                                            src={image.url}
                                                            alt={
                                                                image.description ||
                                                                `Image ${index + 1}`
                                                            }
                                                            className="w-full h-full object-cover"
                                                        />
                                                    </a>
                                                ))}
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>
                                )}
                            </Accordion>
                        </CardContent>
                    </Card>
                </CollapsibleContent>
            </Collapsible>
            {/* 报告卡片（顶部，全宽） */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-2xl">
                            {report && currentStep === RESEARCH_STEPS.length - 1
                                ? "📄 研究报告"
                                : "📝 实时报告"}
                        </CardTitle>
                        <div className="flex items-center gap-2">
                            {isConnected &&
                                currentStep === 4 &&
                                !isReportComplete && (
                                    <Loader variant="dots" size="sm" />
                                )}
                            {report && (
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleDownload}
                                    className="gap-2"
                                >
                                    <Download className="w-4 h-4" />
                                    下载报告
                                </Button>
                            )}
                        </div>
                    </div>
                    {query && !isReportComplete && (
                        <p className="text-sm text-muted-foreground mt-2">
                            正在研究：{query}
                        </p>
                    )}
                </CardHeader>
                <CardContent>
                    {!report && !isConnected && (
                        <div className="text-center py-12 text-gray-400">
                            <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p className="text-lg">等待报告生成...</p>
                        </div>
                    )}

                    {isConnected && !report && currentStep < 4 && (
                        <div className="text-center py-12">
                            <Loader variant="pulse-dot" size="lg" />
                            <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                                正在准备报告...
                            </p>
                        </div>
                    )}

                    {report && (
                        <div className="prose prose-lg dark:prose-invert max-w-none">
                            <Markdown id="live-report">{report}</Markdown>

                            {/* Loading 状态 - 只在生成过程中显示 */}
                            {!isReportComplete && (
                                <div className="flex items-center gap-2 mt-4 text-sm text-muted-foreground animate-in fade-in duration-300">
                                    <CircularLoader size="sm" className="!text-blue-500" />
                                    <span>正在生成报告...</span>
                                </div>
                            )}

                            <div ref={reportEndRef} />
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
