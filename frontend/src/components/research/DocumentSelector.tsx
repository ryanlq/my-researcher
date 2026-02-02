"use client"

import { useEffect, useState } from "react"
import { FileText, Trash2, RefreshCw, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { listDocuments, deleteDocument, type Document } from "@/lib/api"
import { DocumentUploader } from "./DocumentUploader"

interface DocumentSelectorProps {
  selectedIds: string[]
  onChange: (ids: string[]) => void
  disabled?: boolean
}

const FILE_TYPE_ICONS: Record<string, string> = {
  pdf: '📕',
  text: '📄',
  csv: '📊',
  excel: '📈',
  markdown: '📝',
  powerpoint: '📽️',
  word: '📜',
}

export function DocumentSelector({
  selectedIds,
  onChange,
  disabled = false
}: DocumentSelectorProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadDocuments = async () => {
    setLoading(true)
    setError(null)
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err: any) {
      setError(err.message || '加载文档列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const handleToggle = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter(sid => sid !== id))
    } else {
      onChange([...selectedIds, id])
    }
  }

  const handleSelectAll = () => {
    if (selectedIds.length === documents.length) {
      onChange([])
    } else {
      onChange(documents.map(d => d.id))
    }
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await deleteDocument(id)
      // 从已选列表中移除
      onChange(selectedIds.filter(sid => sid !== id))
      // 重新加载列表
      await loadDocuments()
    } catch (err: any) {
      alert(err.message || '删除失败')
    }
  }

  const handleUploadSuccess = () => {
    loadDocuments()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-4">
      {/* 上传文档 */}
      <DocumentUploader
        onUploadSuccess={handleUploadSuccess}
        disabled={disabled}
      />

      {/* 文档列表 */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">
            已上传文档 {documents.length > 0 && `(${documents.length})`}
          </Label>
          <div className="flex items-center gap-2">
            {documents.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectAll}
                disabled={disabled}
              >
                {selectedIds.length === documents.length ? '取消全选' : '全选'}
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={loadDocuments}
              disabled={loading || disabled}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {loading && documents.length === 0 ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            加载中...
          </div>
        ) : error ? (
          <div className="text-center py-8 text-sm text-destructive">
            {error}
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            暂无文档，请先上传
          </div>
        ) : (
          <ScrollArea className="h-[300px] rounded-md border">
            <div className="p-2 space-y-1">
              {documents.map((doc) => {
                const isSelected = selectedIds.includes(doc.id)
                const icon = FILE_TYPE_ICONS[doc.file_type] || '📄'

                return (
                  <div
                    key={doc.id}
                    className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                      isSelected ? 'bg-primary/10' : 'hover:bg-accent'
                    } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    onClick={() => !disabled && handleToggle(doc.id)}
                  >
                    <Checkbox
                      checked={isSelected}
                      onChange={() => handleToggle(doc.id)}
                      disabled={disabled}
                    />

                    <span className="text-2xl">{icon}</span>

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {doc.original_filename}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(doc.file_size)} • {formatDate(doc.uploaded_at)}
                      </p>
                    </div>

                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 flex-shrink-0"
                      onClick={(e) => handleDelete(doc.id, e)}
                      disabled={disabled}
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </Button>
                  </div>
                )
              })}
            </div>
          </ScrollArea>
        )}

        {/* 已选择提示 */}
        {selectedIds.length > 0 && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-primary/10 border border-primary/20">
            <Check className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">
              已选择 {selectedIds.length} 个文档
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
