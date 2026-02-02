export type ResearchStatus = 'running' | 'completed' | 'error';
export type ReportFormat = 'markdown' | 'pdf' | 'docx' | 'html';
export type ReportType = 'research_report' | 'deep' | 'multi_agent';

// ✨ 新增：研究来源类型
export type ReportSource = 'web' | 'static' | 'local' | 'hybrid';

export interface Research {
  query: string;
  report_type: string;
  status: ResearchStatus;
  report: string | null;
  sources: string[];
  costs: number;
  images: string[];
  progress?: ResearchProgress;
  // ✨ 新增：指定来源相关字段
  report_source?: ReportSource;
  source_urls?: string[];
  complement_source_urls?: boolean;
  document_ids?: string[];  // ✨ 新增：文档ID列表
}

export interface ResearchProgress {
  status: ResearchStatus;
  current_query?: string;
  message?: string;
}

export interface ResearchRequest {
  query: string;
  report_type?: ReportType;
  report_format?: string;
  tone?: string;
  language?: string;
  // ✨ 新增：指定来源研究字段
  report_source?: ReportSource;
  source_urls?: string[];
  complement_source_urls?: boolean;
  document_ids?: string[];  // ✨ 新增：文档ID列表
}

export interface CostEstimate {
  estimated_cost: number;
  estimated_time_minutes: number;
  estimated_queries: number;
}

export interface WebSocketEvent {
  event: string;
  [key: string]: any;
}
