"use client";

import { Markdown } from "@/components/ui/markdown";
import { Badge } from "@/components/ui/badge";
import { FileText, CheckCircle2, Clock, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Globe, Image as ImageIcon } from "lucide-react";

interface Source {
    url: string;
    title?: string;
}

interface Image {
    url: string;
    description?: string;
}

interface ResearchReportProps {
    query: string;
    report: string;
    sources: string[];
    costs: number;
    images: string[];
    reportType?: string;
    status: string;
    onNewResearch?: () => void;
}

export function ResearchReport({
    query,
    report,
    sources,
    costs,
    images,
    reportType,
    status,
    onNewResearch,
}: ResearchReportProps) {
    const getStatusConfig = () => {
        switch (status) {
            case "completed":
                return {
                    icon: CheckCircle2,
                    label: "已完成",
                    color: "text-green-500",
                    bgColor: "bg-green-500/10",
                };
            case "error":
                return {
                    icon: Clock,
                    label: "失败",
                    color: "text-red-500",
                    bgColor: "bg-red-500/10",
                };
            default:
                return {
                    icon: Clock,
                    label: "未知",
                    color: "text-gray-500",
                    bgColor: "bg-gray-500/10",
                };
        }
    };

    const statusConfig = getStatusConfig();
    const StatusIcon = statusConfig.icon;

    // 下载报告为 Markdown 文件
    const handleDownload = () => {
        // 创建文件内容（包含元数据）
        const content = `# ${query}

**生成时间:** ${new Date().toLocaleString('zh-CN')}
**来源数量:** ${sources.length}
**成本:** $${costs.toFixed(4)}
**报告类型:** ${reportType === "research_report" ? "标准研究" : reportType === "deep" ? "深度研究" : "多智能体"}

---

## 参考来源

${sources.map((source, index) => `${index + 1}. ${source}`).join('\n')}

${images.length > 0 ? `
## 相关图片

${images.map((url, index) => `${index + 1}. ${url}`).join('\n')}
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

    return (
        <div className="w-full space-y-6">
            {/* 研究信息卡片 */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                            <FileText className="w-5 h-5" />
                            <span>研究报告</span>
                        </CardTitle>
                        <div className="flex items-center gap-2">
                            <span
                                className={`flex items-center gap-1 ${statusConfig.color} ${statusConfig.bgColor} px-2 py-1 rounded text-sm`}
                            >
                                <StatusIcon className="w-3.5 h-3.5" />
                                {statusConfig.label}
                            </span>
                            {reportType && (
                                <Badge variant="outline" className="text-xs">
                                    {reportType === "research_report"
                                        ? "标准研究"
                                        : reportType === "deep"
                                          ? "深度研究"
                                          : "多智能体"}
                                </Badge>
                            )}
                        </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
                        <span>{sources.length} 个来源</span>
                        <span>•</span>
                        <span>${costs.toFixed(4)}</span>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="mb-4 p-3 bg-muted rounded-md">
                        <p className="text-sm font-medium">研究问题：</p>
                        <p className="text-sm text-muted-foreground mt-1">
                            {query}
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* 报告卡片 */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>研究内容</CardTitle>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleDownload}
                            className="gap-2"
                        >
                            <Download className="w-4 h-4" />
                            下载报告
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="prose prose-lg dark:prose-invert max-w-none p-6">
                        <Markdown id="cached-report">{report}</Markdown>
                    </div>
                </CardContent>
            </Card>

            {/* 参考来源 */}
            {sources.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Globe className="w-5 h-5" />
                            <span>参考来源 ({sources.length})</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-wrap gap-2">
                            {sources.map((source, index) => (
                                <a
                                    key={`${source}-${index}`}
                                    href={source}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs"
                                >
                                    <Badge
                                        variant="outline"
                                        className="hover:bg-accent"
                                    >
                                        {source.length > 50
                                            ? source.substring(0, 50) + "..."
                                            : source}
                                    </Badge>
                                </a>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* 图片 */}
            {images.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <ImageIcon className="w-5 h-5" />
                            <span>相关图片 ({images.length})</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-3 gap-2">
                            {images.map((img, index) => (
                                <a
                                    key={`img-${index}`}
                                    href={img}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="aspect-video bg-muted rounded overflow-hidden hover:bg-accent transition-colors"
                                >
                                    <img
                                        src={img}
                                        alt={`研究图片 ${index + 1}`}
                                        className="w-full h-full object-cover"
                                    />
                                </a>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
