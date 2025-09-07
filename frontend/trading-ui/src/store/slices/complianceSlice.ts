import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ComplianceRule {
  id: string;
  name: string;
  description: string;
  type: 'limit' | 'restriction' | 'validation';
  category: 'sebi' | 'rbi' | 'fema' | 'internal';
  status: 'active' | 'inactive' | 'suspended';
  parameters: Record<string, any>;
  lastUpdated: string;
}

interface ComplianceViolation {
  id: string;
  ruleId: string;
  ruleName: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  details: Record<string, any>;
  timestamp: string;
  status: 'active' | 'investigating' | 'resolved' | 'false_positive';
  assignedTo?: string;
  resolvedAt?: string;
  resolvedBy?: string;
  resolution?: string;
  orderId?: string;
  tradeId?: string;
  userId?: string;
}

interface RegulatoryReport {
  id: string;
  type: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annual' | 'ad_hoc';
  category: 'sebi' | 'rbi' | 'fema' | 'internal';
  name: string;
  description: string;
  status: 'draft' | 'pending_review' | 'approved' | 'submitted' | 'acknowledged';
  generatedAt: string;
  reviewedAt?: string;
  submittedAt?: string;
  dueDate: string;
  data: Record<string, any>;
  fileSize?: number;
  filePath?: string;
}

interface AuditTrail {
  id: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  resourceId?: string;
  details: Record<string, any>;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  success: boolean;
  errorMessage?: string;
}

interface ComplianceState {
  rules: ComplianceRule[];
  violations: ComplianceViolation[];
  reports: RegulatoryReport[];
  auditTrail: AuditTrail[];
  complianceStatus: {
    overallStatus: 'compliant' | 'warning' | 'violation';
    activeViolations: number;
    pendingReports: number;
    lastAuditDate?: string;
    nextAuditDue?: string;
  };
  monitoringEnabled: boolean;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  selectedViolation: ComplianceViolation | null;
  selectedReport: RegulatoryReport | null;
}

const initialState: ComplianceState = {
  rules: [],
  violations: [],
  reports: [],
  auditTrail: [],
  complianceStatus: {
    overallStatus: 'compliant',
    activeViolations: 0,
    pendingReports: 0,
  },
  monitoringEnabled: true,
  isLoading: false,
  error: null,
  lastUpdated: null,
  selectedViolation: null,
  selectedReport: null,
};

const complianceSlice = createSlice({
  name: 'compliance',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setComplianceRules: (state, action: PayloadAction<ComplianceRule[]>) => {
      state.rules = action.payload;
      state.lastUpdated = new Date().toISOString();
      state.isLoading = false;
    },
    addComplianceRule: (state, action: PayloadAction<ComplianceRule>) => {
      const existingIndex = state.rules.findIndex(rule => rule.id === action.payload.id);
      if (existingIndex !== -1) {
        state.rules[existingIndex] = action.payload;
      } else {
        state.rules.push(action.payload);
      }
      state.lastUpdated = new Date().toISOString();
    },
    updateComplianceRule: (state, action: PayloadAction<ComplianceRule>) => {
      const index = state.rules.findIndex(rule => rule.id === action.payload.id);
      if (index !== -1) {
        state.rules[index] = action.payload;
        state.lastUpdated = new Date().toISOString();
      }
    },
    setViolations: (state, action: PayloadAction<ComplianceViolation[]>) => {
      state.violations = action.payload;
      state.complianceStatus.activeViolations = action.payload.filter(v => v.status === 'active').length;
      state.complianceStatus.overallStatus = state.complianceStatus.activeViolations > 0 ? 'violation' : 'compliant';
      state.lastUpdated = new Date().toISOString();
    },
    addViolation: (state, action: PayloadAction<ComplianceViolation>) => {
      state.violations.unshift(action.payload);
      state.complianceStatus.activeViolations = state.violations.filter(v => v.status === 'active').length;
      state.complianceStatus.overallStatus = state.complianceStatus.activeViolations > 0 ? 'violation' : 'compliant';
      state.lastUpdated = new Date().toISOString();
    },
    updateViolation: (state, action: PayloadAction<ComplianceViolation>) => {
      const index = state.violations.findIndex(v => v.id === action.payload.id);
      if (index !== -1) {
        state.violations[index] = action.payload;
        state.complianceStatus.activeViolations = state.violations.filter(v => v.status === 'active').length;
        state.complianceStatus.overallStatus = state.complianceStatus.activeViolations > 0 ? 'violation' : 'compliant';
        state.lastUpdated = new Date().toISOString();
        
        // Update selected violation if it's the same
        if (state.selectedViolation?.id === action.payload.id) {
          state.selectedViolation = action.payload;
        }
      }
    },
    resolveViolation: (state, action: PayloadAction<{
      id: string;
      resolution: string;
      resolvedBy: string;
    }>) => {
      const { id, resolution, resolvedBy } = action.payload;
      const violation = state.violations.find(v => v.id === id);
      
      if (violation) {
        violation.status = 'resolved';
        violation.resolution = resolution;
        violation.resolvedBy = resolvedBy;
        violation.resolvedAt = new Date().toISOString();
        
        state.complianceStatus.activeViolations = state.violations.filter(v => v.status === 'active').length;
        state.complianceStatus.overallStatus = state.complianceStatus.activeViolations > 0 ? 'violation' : 'compliant';
        state.lastUpdated = new Date().toISOString();
      }
    },
    setReports: (state, action: PayloadAction<RegulatoryReport[]>) => {
      state.reports = action.payload;
      state.complianceStatus.pendingReports = action.payload.filter(r => ['draft', 'pending_review'].includes(r.status)).length;
      state.lastUpdated = new Date().toISOString();
    },
    addReport: (state, action: PayloadAction<RegulatoryReport>) => {
      const existingIndex = state.reports.findIndex(r => r.id === action.payload.id);
      if (existingIndex !== -1) {
        state.reports[existingIndex] = action.payload;
      } else {
        state.reports.unshift(action.payload);
      }
      
      state.complianceStatus.pendingReports = state.reports.filter(r => ['draft', 'pending_review'].includes(r.status)).length;
      state.lastUpdated = new Date().toISOString();
    },
    updateReport: (state, action: PayloadAction<RegulatoryReport>) => {
      const index = state.reports.findIndex(r => r.id === action.payload.id);
      if (index !== -1) {
        state.reports[index] = action.payload;
        state.complianceStatus.pendingReports = state.reports.filter(r => ['draft', 'pending_review'].includes(r.status)).length;
        state.lastUpdated = new Date().toISOString();
        
        // Update selected report if it's the same
        if (state.selectedReport?.id === action.payload.id) {
          state.selectedReport = action.payload;
        }
      }
    },
    setAuditTrail: (state, action: PayloadAction<AuditTrail[]>) => {
      state.auditTrail = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addAuditEntry: (state, action: PayloadAction<AuditTrail>) => {
      state.auditTrail.unshift(action.payload);
      // Keep only last 1000 entries
      if (state.auditTrail.length > 1000) {
        state.auditTrail = state.auditTrail.slice(0, 1000);
      }
      state.lastUpdated = new Date().toISOString();
    },
    setSelectedViolation: (state, action: PayloadAction<ComplianceViolation | null>) => {
      state.selectedViolation = action.payload;
    },
    setSelectedReport: (state, action: PayloadAction<RegulatoryReport | null>) => {
      state.selectedReport = action.payload;
    },
    setMonitoringEnabled: (state, action: PayloadAction<boolean>) => {
      state.monitoringEnabled = action.payload;
    },
    updateComplianceStatus: (state, action: PayloadAction<Partial<ComplianceState['complianceStatus']>>) => {
      state.complianceStatus = { ...state.complianceStatus, ...action.payload };
      state.lastUpdated = new Date().toISOString();
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearComplianceData: (state) => {
      state.rules = [];
      state.violations = [];
      state.reports = [];
      state.auditTrail = [];
      state.complianceStatus = {
        overallStatus: 'compliant',
        activeViolations: 0,
        pendingReports: 0,
      };
      state.selectedViolation = null;
      state.selectedReport = null;
      state.lastUpdated = null;
    },
  },
});

export const {
  setLoading,
  setComplianceRules,
  addComplianceRule,
  updateComplianceRule,
  setViolations,
  addViolation,
  updateViolation,
  resolveViolation,
  setReports,
  addReport,
  updateReport,
  setAuditTrail,
  addAuditEntry,
  setSelectedViolation,
  setSelectedReport,
  setMonitoringEnabled,
  updateComplianceStatus,
  setError,
  clearError,
  clearComplianceData,
} = complianceSlice.actions;

export default complianceSlice.reducer;
