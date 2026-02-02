"use client"

import { useState } from "react"
import { Plus, X, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"

interface UrlInputListProps {
  urls: string[]
  onChange: (urls: string[]) => void
  complementSourceUrls?: boolean
  onComplementChange?: (enabled: boolean) => void
  disabled?: boolean
}

export function UrlInputList({
  urls,
  onChange,
  complementSourceUrls = false,
  onComplementChange,
  disabled = false
}: UrlInputListProps) {
  const [newUrl, setNewUrl] = useState("")

  const isValidUrl = (url: string) => {
    if (!url) return false
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const addUrl = () => {
    const trimmed = newUrl.trim()
    if (!trimmed) return

    // 自动添加 https:// 前缀
    let urlToAdd = trimmed
    if (!/^https?:\/\//i.test(trimmed)) {
      urlToAdd = `https://${trimmed}`
    }

    if (!isValidUrl(urlToAdd)) {
      alert("请输入有效的URL地址")
      return
    }

    if (urls.includes(urlToAdd)) {
      alert("该URL已添加")
      return
    }

    onChange([...urls, urlToAdd])
    setNewUrl("")
  }

  const removeUrl = (index: number) => {
    onChange(urls.filter((_, i) => i !== index))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault()
      addUrl()
    }
  }

  return (
    <div className="space-y-3">
      <div className="space-y-2">
        <Label className="text-sm font-medium">
          指定研究URL {urls.length > 0 && `(${urls.length})`}
        </Label>

        {/* URL输入框 */}
        <div className="flex gap-2">
          <Input
            placeholder="输入URL，例如: example.com"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled}
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={addUrl}
            disabled={disabled || !newUrl.trim()}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {/* 已添加的URL列表 */}
        {urls.length > 0 && (
          <div className="space-y-2 mt-3">
            {urls.map((url, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-2 rounded-lg border bg-card"
              >
                <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                <span className="flex-1 text-sm truncate">{url}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => removeUrl(index)}
                  disabled={disabled}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 补充搜索选项 */}
      {urls.length > 0 && onComplementChange && (
        <div className="flex items-center space-x-2 p-3 rounded-lg border bg-accent/10">
          <Checkbox
            id="complement"
            checked={complementSourceUrls}
            onCheckedChange={(checked) => onComplementChange(checked as boolean)}
            disabled={disabled}
          />
          <div className="flex-1">
            <Label htmlFor="complement" className="cursor-pointer text-sm">
              在指定URL外进行全网补充搜索
            </Label>
            <p className="text-xs text-muted-foreground mt-1">
              开启后，系统会在您指定的URL基础上，继续搜索其他相关资料
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
