"use client"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarHeader,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Plus, FolderOpen, Search } from "lucide-react"
import { useResearchStore } from "@/stores/research"
import { useEffect, useState } from "react"
import { ProjectListItem } from "./ProjectListItem"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

export function ResearchSidebar() {
  const { history, historyLoading, loadHistory, loadFromHistory, deleteFromHistory, startNewResearch, selectedHistoryId, searchHistory } = useResearchStore()
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<typeof history>([])
  const [isSearching, setIsSearching] = useState(false)

  // 组件挂载时加载历史记录
  useEffect(() => {
    loadHistory()
  }, [])

  // 搜索处理
  useEffect(() => {
    const handleSearch = async () => {
      if (!searchQuery.trim()) {
        setSearchResults([])
        setIsSearching(false)
        return
      }

      setIsSearching(true)
      try {
        const results = await searchHistory(searchQuery)
        setSearchResults(results)
      } catch (error) {
        console.error('Search failed:', error)
        setSearchResults([])
      }
    }

    const debounceTimer = setTimeout(handleSearch, 300)
    return () => clearTimeout(debounceTimer)
  }, [searchQuery, searchHistory])

  // 显示的列表（搜索结果或全部历史）
  const displayList = isSearching ? searchResults : history

  return (
    <Sidebar>
      <SidebarHeader className="border-b pb-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">研究项目</h2>
          <SidebarTrigger />
        </div>
      </SidebarHeader>

      <SidebarContent className="gap-4">
        {/* 搜索框 */}
        <div className="px-3">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索研究..."
              className="pl-8 h-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* 历史记录列表 */}
        <SidebarGroup>
          <SidebarGroupLabel>
            {isSearching ? `搜索结果 (${searchResults.length})` : `最近研究 (${history.length})`}
          </SidebarGroupLabel>
          <SidebarMenu className="gap-1">
            {historyLoading ? (
              // 加载骨架屏
              Array.from({ length: 3 }).map((_, i) => (
                <SidebarMenuItem key={i}>
                  <div className="w-full p-3 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </SidebarMenuItem>
              ))
            ) : displayList.length === 0 ? (
              <SidebarMenuItem>
                <div className="px-2 py-8 text-sm text-muted-foreground text-center">
                  {isSearching ? '未找到匹配的研究' : '暂无研究项目'}
                </div>
              </SidebarMenuItem>
            ) : (
              displayList.map((project) => (
                <SidebarMenuItem key={project.id}>
                  <ProjectListItem
                    project={project}
                    isSelected={selectedHistoryId === project.id}
                    onClick={() => loadFromHistory(project.id)}
                    onDelete={() => deleteFromHistory(project.id)}
                  />
                </SidebarMenuItem>
              ))
            )}

            {/* 新建研究按钮 */}
            <SidebarMenuItem>
              <button
                onClick={startNewResearch}
                className="w-full text-left px-3 py-2 rounded-md text-sm font-medium text-primary hover:bg-accent transition-colors flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                <span>新建研究</span>
              </button>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>

        {/* 组织分组（占位） */}
        <SidebarGroup>
          <SidebarGroupLabel>组织</SidebarGroupLabel>
          <SidebarMenu>
            <SidebarMenuItem>
              <button className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors flex items-center gap-2 text-muted-foreground">
                <FolderOpen className="h-4 w-4" />
                <span>所有项目</span>
                <span className="ml-auto text-xs bg-muted px-1.5 py-0.5 rounded">{history.length}</span>
              </button>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
