/**
 * IndexedDB 相关类型定义
 */

export interface ResearchRecord {
  id: number;
  query: string;
  report_type: string;
  status: 'completed' | 'error';
  report: string;
  sources: string[];
  costs: number;
  images: string[];
  createdAt: string;
  completedAt: string;

  // 展示用元数据
  title: string;
  wordCount: number;
  preview: string;
}

export interface StorageStats {
  totalCount: number;
  totalSize: number; // bytes
  oldestRecord?: Date;
  newestRecord?: Date;
}
