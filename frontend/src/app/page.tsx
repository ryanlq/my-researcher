"use client"

import { useState } from "react"
import { useResearchStore } from "@/stores/research"
import { ResearchSidebar } from "@/components/sidebar/ResearchSidebar"
import { ResearchPromptInput } from "@/components/prompt/ResearchPromptInput"
import ResearchProgressPromptKit from "@/components/ResearchProgressPromptKit"
import { ResearchReport } from "@/components/ResearchReport"
import { Settings, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Research, ReportType } from "@/types/research"

export default function Home() {
  const { viewState, currentResearch, startNewResearch, updateResearch, setError } = useResearchStore()
  const [settingsOpen, setSettingsOpen] = useState(false)

  // 研究开始的回调
  const handleResearchStart = () => {
    const store = useResearchStore.getState()
    console.log("研究开始", { currentResearch: store.currentResearch })
  }

  // 研究完成的回调
  const handleResearchComplete = (data: { report: string; sources: any[]; images: any[]; costs: number }) => {
    console.log("研究完成，报告长度:", data.report.length)
    console.log("当前 currentResearch:", currentResearch)

    // 更新当前研究状态
    updateResearch({
      status: "completed" as const,
      report: data.report,
      sources: data.sources.map((s: any) => typeof s === 'string' ? s : s.url),
      costs: data.costs,
      images: data.images,
    })

    // 获取 query
    const query = currentResearch?.query

    if (!query) {
      console.error("❌ 无法保存到历史记录：query 为空", { currentResearch })
      return
    }

    console.log("💾 准备保存到历史记录:", {
      query,
      reportLength: data.report.length,
      costs: data.costs,
    })

    // 保存到历史记录
    const { saveToHistory } = useResearchStore.getState()
    saveToHistory({
      query: query,
      report_type: currentResearch.report_type || "research_report",
      status: "completed",
      report: data.report,
      sources: data.sources.map((s: any) => typeof s === 'string' ? s : s.url),
      costs: data.costs,
      images: data.images.map((img: any) => img.url || img),
    })
  }

  // 研究失败的回调
  const handleResearchError = (error: string) => {
    console.error("研究失败:", error)
    setError(error)

    // 保存失败的研究到历史记录
    const store = useResearchStore.getState()
    if (currentResearch) {
      store.saveToHistory({
        query: currentResearch.query,
        report_type: currentResearch.report_type || "research_report",
        status: "error",
        report: `研究失败：${error}`,
        sources: [],
        costs: 0,
        images: [],
      })
    }
  }

  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen overflow-hidden">
        {/* 左侧：可收缩的侧边栏 */}
        <ResearchSidebar />

        {/* 右侧：主内容区 */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* 顶部栏：Logo + 新研究按钮 */}
          <header className="h-14 border-b flex items-center justify-between px-4 bg-background">
            <div className="flex items-center gap-2">
              <SidebarTrigger />
              <h1 className="text-xl font-semibold">GPT-Researcher</h1>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSettingsOpen(true)}
              >
                <Settings className="h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={startNewResearch}
              >
                <Plus className="h-4 w-4 mr-2" />
                新研究
              </Button>
            </div>
          </header>

          {/* 内容区：根据 viewState 切换 */}
          <main className="flex-1 overflow-auto">
            {viewState === 'input' ? (
              // 状态 1：居中的输入界面
              <div className="h-full flex items-center justify-center bg-background">
                <ResearchPromptInput />
              </div>
            ) : (
              // 状态 2：显示研究内容
              <div className="h-full bg-background p-4">
                {currentResearch && (
                  currentResearch.status === 'completed' ? (
                    // 已完成：显示只读报告
                    <ResearchReport
                      query={currentResearch.query}
                      report={currentResearch.report || ''}
                      sources={currentResearch.sources}
                      costs={currentResearch.costs}
                      images={currentResearch.images}
                      reportType={currentResearch.report_type}
                      status={currentResearch.status}
                      onNewResearch={startNewResearch}
                    />
                  ) : (
                    // 进行中：显示实时进度
                    <ResearchProgressPromptKit
                      query={currentResearch.query}
                      reportType={currentResearch.report_type}
                      reportSource={currentResearch.report_source}
                      sourceUrls={currentResearch.source_urls}
                      complementSourceUrls={currentResearch.complement_source_urls}
                      documentIds={currentResearch.document_ids}
                      onStart={handleResearchStart}
                      onComplete={handleResearchComplete}
                      onError={handleResearchError}
                    />
                  )
                )}
              </div>
            )}
          </main>
        </div>
      </div>

      {/* TODO: 设置对话框 */}
      {settingsOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-background border rounded-lg shadow-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">设置</h2>
            <p className="text-muted-foreground mb-4">设置功能即将推出...</p>
            <Button onClick={() => setSettingsOpen(false)}>关闭</Button>
          </div>
        </div>
      )}
    </SidebarProvider>
  )
}
