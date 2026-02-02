"use client"

import { ResearchRecord } from '@/types/indexeddb';
import { FileText, CheckCircle2, XCircle, Clock, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useState } from 'react';

interface ProjectListItemProps {
  project: ResearchRecord;
  isSelected: boolean;
  onClick: () => void;
  onDelete: () => void;
}

/**
 * 格式化时间显示
 */
function formatTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins} 分钟前`;
  if (diffHours < 24) return `${diffHours} 小时前`;
  if (diffDays < 7) return `${diffDays} 天前`;

  // 超过一周显示完整日期
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

/**
 * 格式化字数
 */
function formatWordCount(count: number): string {
  if (count < 1000) return `${count} 字`;
  return `${(count / 1000).toFixed(1)}k 字`;
}

/**
 * 格式化费用
 */
function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}

/**
 * 获取状态配置
 */
function getStatusConfig(status: ResearchRecord['status']) {
  switch (status) {
    case 'completed':
      return {
        icon: CheckCircle2,
        label: '已完成',
        color: 'text-green-500',
        bgColor: 'bg-green-500/10',
      };
    case 'error':
      return {
        icon: XCircle,
        label: '失败',
        color: 'text-red-500',
        bgColor: 'bg-red-500/10',
      };
    default:
      return {
        icon: Clock,
        label: '未知',
        color: 'text-gray-500',
        bgColor: 'bg-gray-500/10',
      };
  }
}

export function ProjectListItem({ project, isSelected, onClick, onDelete }: ProjectListItemProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const statusConfig = getStatusConfig(project.status);
  const StatusIcon = statusConfig.icon;

  const handleDelete = () => {
    onDelete();
    setDeleteDialogOpen(false);
  };

  return (
    <div className={`group relative rounded-lg transition-all ${isSelected ? 'bg-accent' : 'hover:bg-accent/50'}`}>
      <button
        onClick={onClick}
        className="w-full text-left p-3"
      >
        {/* 标题行 */}
        <div className="flex items-start gap-2 mb-2">
          <FileText className={`h-4 w-4 mt-0.5 flex-shrink-0 ${statusConfig.color}`} />
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-medium truncate">{project.title}</h3>
          </div>
        </div>

        {/* 状态信息行 */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground pl-6">
          <span className={`flex items-center gap-1 ${statusConfig.color} ${statusConfig.bgColor} px-1.5 py-0.5 rounded`}>
            <StatusIcon className="h-3 w-3" />
            {statusConfig.label}
          </span>
          <span>•</span>
          <span>{formatWordCount(project.wordCount)}</span>
          <span>•</span>
          <span>{formatCost(project.costs)}</span>
        </div>

        {/* 时间行 */}
        <div className="text-xs text-muted-foreground pl-6 mt-1">
          {formatTime(project.createdAt)}
        </div>

        {/* 预览（仅已完成项目） */}
        {project.status === 'completed' && project.preview && (
          <div className="text-xs text-muted-foreground pl-6 mt-1.5 line-clamp-2">
            {project.preview}
          </div>
        )}
      </button>

      {/* 删除按钮 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-2 right-2 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive" />
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>删除研究记录</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除 "{project.title}" 吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
