import { create } from 'zustand';
import { Research, ResearchProgress, ReportSource } from '@/types/research';
import { ResearchRecord } from '@/types/indexeddb';
import { researchDB } from '@/lib/indexeddb';

interface ResearchStore {
  // 状态
  currentResearch: Research | null;
  progress: ResearchProgress | null;
  isLoading: boolean;
  error: string | null;
  viewState: 'input' | 'progress';  // 视图状态

  // 历史记录相关状态
  history: ResearchRecord[];
  historyLoading: boolean;
  selectedHistoryId: number | null;

  // 操作
  setCurrentResearch: (research: Research | null) => void;
  setProgress: (progress: ResearchProgress | null) => void;
  updateResearch: (updates: Partial<Research>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setViewState: (state: 'input' | 'progress') => void;  // 设置视图状态
  startNewResearch: () => void;  // 开始新研究（重置到输入状态）
  clear: () => void;

  // 历史记录操作
  saveToHistory: (research: Omit<ResearchRecord, 'id' | 'createdAt' | 'completedAt' | 'title' | 'wordCount' | 'preview'>) => Promise<void>;
  loadHistory: () => Promise<void>;
  loadFromHistory: (id: number) => Promise<void>;
  deleteFromHistory: (id: number) => Promise<void>;
  searchHistory: (keyword: string) => Promise<ResearchRecord[]>;
}

export const useResearchStore = create<ResearchStore>((set, get) => ({
  // 初始状态
  currentResearch: null,
  progress: null,
  isLoading: false,
  error: null,
  viewState: 'input',  // 默认为输入状态

  // 历史记录初始状态
  history: [],
  historyLoading: false,
  selectedHistoryId: null,

  // 操作
  setCurrentResearch: (research) => set({ currentResearch: research }),

  setProgress: (progress) => set({ progress }),

  updateResearch: (updates) =>
    set((state) => ({
      currentResearch: state.currentResearch
        ? { ...state.currentResearch, ...updates }
        : null,
    })),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  setViewState: (viewState) => set({ viewState }),

  startNewResearch: () => set({
    currentResearch: null,
    progress: null,
    isLoading: false,
    error: null,
    viewState: 'input',  // 重置到输入状态
    selectedHistoryId: null,  // 清除历史选择
  }),

  clear: () => set({
    currentResearch: null,
    progress: null,
    isLoading: false,
    error: null,
    viewState: 'input',
    selectedHistoryId: null,
  }),

  // 历史记录操作

  /**
   * 保存到历史记录
   */
  saveToHistory: async (research) => {
    try {
      const id = await researchDB.saveResearch(research);
      console.log('✅ Research saved to history:', id);

      // 刷新历史列表
      get().loadHistory();
    } catch (error) {
      console.error('❌ Failed to save to history:', error);
    }
  },

  /**
   * 加载历史记录列表
   */
  loadHistory: async () => {
    set({ historyLoading: true });
    try {
      const records = await researchDB.getAllResearches();
      set({ history: records, historyLoading: false });
    } catch (error) {
      console.error('❌ Failed to load history:', error);
      set({ historyLoading: false });
    }
  },

  /**
   * 从历史记录加载研究详情
   */
  loadFromHistory: async (id: number) => {
    try {
      const record = await researchDB.getResearch(id);

      if (!record) {
        console.error('❌ Research not found:', id);
        return;
      }

      // 设置当前研究
      set({
        currentResearch: {
          query: record.query,
          report_type: record.report_type,
          status: record.status,
          report: record.report,
          sources: record.sources,
          costs: record.costs,
          images: record.images,
        },
        viewState: 'progress',
        selectedHistoryId: id,
        error: null,
      });
    } catch (error) {
      console.error('❌ Failed to load from history:', error);
      set({ error: '加载历史记录失败' });
    }
  },

  /**
   * 删除历史记录
   */
  deleteFromHistory: async (id: number) => {
    try {
      await researchDB.deleteResearch(id);
      console.log('✅ Research deleted from history:', id);

      // 如果删除的是当前选中的，清空选择
      const state = get();
      if (state.selectedHistoryId === id) {
        set({ selectedHistoryId: null });
      }

      // 刷新历史列表
      get().loadHistory();
    } catch (error) {
      console.error('❌ Failed to delete from history:', error);
    }
  },

  /**
   * 搜索历史记录
   */
  searchHistory: async (keyword: string) => {
    try {
      const results = await researchDB.searchResearches(keyword);
      return results;
    } catch (error) {
      console.error('❌ Failed to search history:', error);
      return [];
    }
  },
}));
