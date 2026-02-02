"use client"

import { useCallback, useState } from "react"
import { Upload, FileText, X, Check, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { uploadDocument, type Document } from "@/lib/api"

interface UploadStatus {
  file: File
  status: 'uploading' | 'success' | 'error'
  progress: number
  error?: string
  document?: Document
}

interface DocumentUploaderProps {
  onUploadSuccess?: (document: Document) => void
  disabled?: boolean
  maxSize?: number // MB
}

const MAX_SIZE = 50 * 1024 * 1024 // 50MB

export function DocumentUploader({
  onUploadSuccess,
  disabled = false,
  maxSize = MAX_SIZE
}: DocumentUploaderProps) {
  const [uploads, setUploads] = useState<UploadStatus[]>([])
  const [isDragging, setIsDragging] = useState(false)

  const validateFile = (file: File): string | null => {
    // 检查文件大小
    if (file.size > maxSize) {
      return `文件大小超过限制 (${maxSize / 1024 / 1024}MB)`
    }

    // 检查文件类型
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'text/csv',
      'text/markdown',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]

    // 检查扩展名
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    const allowedExts = ['.pdf', '.txt', '.csv', '.xlsx', '.xls', '.md', '.ppt', '.pptx', '.docx', '.doc']

    if (!allowedExts.includes(ext)) {
      return `不支持的文件类型: ${ext}`
    }

    return null
  }

  const uploadFile = useCallback(async (file: File) => {
    const error = validateFile(file)
    if (error) {
      setUploads(prev => [...prev, {
        file,
        status: 'error',
        progress: 0,
        error
      }])
      return
    }

    const uploadId = Date.now()
    setUploads(prev => [...prev, {
      file,
      status: 'uploading',
      progress: 0
    }])

    try {
      const document = await uploadDocument(file)

      setUploads(prev => prev.map(u =>
        u.file.name === file.name && u.status === 'uploading'
          ? { ...u, status: 'success', progress: 100, document }
          : u
      ))

      onUploadSuccess?.(document)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || '上传失败'

      setUploads(prev => prev.map(u =>
        u.file.name === file.name && u.status === 'uploading'
          ? { ...u, status: 'error', error: errorMessage }
          : u
      ))
    }
  }, [maxSize, onUploadSuccess])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    files.forEach(uploadFile)
  }, [uploadFile])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    files.forEach(uploadFile)
    e.target.value = '' // 重置input
  }, [uploadFile])

  const removeUpload = (index: number) => {
    setUploads(prev => prev.filter((_, i) => i !== index))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="space-y-3">
      {/* 上传区域 */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onDragOver={(e) => {
          e.preventDefault()
          if (!disabled) setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          multiple
          className="hidden"
          onChange={handleFileInput}
          disabled={disabled}
          accept=".pdf,.txt,.csv,.xlsx,.xls,.md,.ppt,.pptx,.docx,.doc"
        />
        <Upload className="h-10 w-10 mx-auto mb-3 text-muted-foreground" />
        <p className="text-sm font-medium">
          拖拽文件到此处或点击上传
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          支持 PDF, TXT, CSV, XLSX, MD, PPT, PPTX, DOCX, DOC (最大 {maxSize / 1024 / 1024}MB)
        </p>
      </div>

      {/* 上传列表 */}
      {uploads.length > 0 && (
        <div className="space-y-2">
          {uploads.map((upload, index) => (
            <Card key={index} className="p-3">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-muted-foreground flex-shrink-0" />

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{upload.file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(upload.file.size)}
                  </p>

                  {upload.status === 'uploading' && (
                    <Progress value={upload.progress} className="h-1 mt-2" />
                  )}

                  {upload.status === 'error' && (
                    <p className="text-xs text-destructive mt-1 flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {upload.error}
                    </p>
                  )}

                  {upload.status === 'success' && (
                    <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                      <Check className="h-3 w-3" />
                      上传成功
                    </p>
                  )}
                </div>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 flex-shrink-0"
                  onClick={() => removeUpload(index)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
