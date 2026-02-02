"use client"

import { ReportSource } from "@/types/research"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

interface SourceSelectorProps {
  value: ReportSource
  onChange: (value: ReportSource) => void
  disabled?: boolean
}

export function SourceSelector({ value, onChange, disabled = false }: SourceSelectorProps) {
  return (
    <div className="space-y-3">
      <Label className="text-sm font-medium">选择研究来源</Label>
      <RadioGroup
        value={value}
        onValueChange={(val) => onChange(val as ReportSource)}
        disabled={disabled}
        className="flex flex-col gap-2"
      >
        <div className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent/50 transition-colors">
          <RadioGroupItem value="web" id="web" />
          <Label htmlFor="web" className="cursor-pointer flex-1">
            <div className="font-medium">标准研究（全网搜索）</div>
            <div className="text-xs text-muted-foreground">
              自动在全网搜索相关资料，适用于大多数研究需求
            </div>
          </Label>
        </div>

        <div className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent/50 transition-colors">
          <RadioGroupItem value="static" id="static" />
          <Label htmlFor="static" className="cursor-pointer flex-1">
            <div className="font-medium">指定来源研究</div>
            <div className="text-xs text-muted-foreground">
              仅研究您指定的URL，成本更低，结果更精准
            </div>
          </Label>
        </div>

        <div className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent/50 transition-colors">
          <RadioGroupItem value="local" id="local" />
          <Label htmlFor="local" className="cursor-pointer flex-1">
            <div className="font-medium">本地文档研究</div>
            <div className="text-xs text-muted-foreground">
              基于您上传的文档进行研究，成本最低
            </div>
          </Label>
        </div>

        <div className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent/50 transition-colors">
          <RadioGroupItem value="hybrid" id="hybrid" />
          <Label htmlFor="hybrid" className="cursor-pointer flex-1">
            <div className="font-medium">混合研究</div>
            <div className="text-xs text-muted-foreground">
              结合指定URL和本地文档进行综合研究
            </div>
          </Label>
        </div>
      </RadioGroup>
    </div>
  )
}
