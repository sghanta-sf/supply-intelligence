import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Boxes,
  FileText,
  BrainCircuit,
  GitBranch,
  ShieldAlert,
  ArrowRightLeft,
  Truck,
  Copy,
  Plus,
  Trash2,
  Key,
  RefreshCw,
  Search,
  Database,
  Activity,
  Sparkles,
  Layers,
  ChevronRight,
  ChevronDown,
  Send,
  Building2,
  UserCheck,
  Zap,
  TrendingUp,
  X,
  SlidersHorizontal,
  Workflow,
  Network,
  BarChart3
} from "lucide-react";

interface KPI {
  label: string;
  value: string | number;
  subtext: string;
  trend: string;
  status: string;
}

interface RiskItem {
  item_id: string;
  item_description: string;
  item_category: string;
  current_on_hand: number;
  avg_daily_usage: number;
  days_of_supply: number;
  risk_score: number;
  risk_tier: string;
  risk_factors: Record<string, any>;
  forecast_demand_30d: number;
  forecast_demand_90d: number;
}

interface RecommendedOrder {
  recommendation_id: number;
  item_id: string;
  item_description: string;
  supplier_id: string;
  supplier_name: string;
  recommended_qty: number;
  unit_cost: number;
  total_cost: number;
  order_reason: string;
  urgency: string;
  confidence_score: number;
  model_reasoning: string;
  facility_id: string;
  facility_name: string;
  comments?: string | null;
  decision_status?: string;
  decision?: string;
}

interface SubstitutionCandidate {
  substitution_id: number;
  shortage_item_id: string;
  shortage_item_description: string;
  alternative_item_id: string;
  alternative_item_description: string;
  clinical_equivalence: string;
  formulary_status: string;
  availability: string;
  agent_reasoning: string;
  confidence_score: number;
}

interface SimFacility {
  facility_id: string;
  facility_name: string;
  patients: number;
  allergy_flags: number;
  contraindications: number;
  units_allocated: number;
  days_cover: number;
  monthly_cost_delta: number;
  lead_time_delta_days: number;
}

interface SimAgentCategory {
  key: string;
  label: string;
  severity: string;
  patients: number;
  share: number;
  recommendation: string;
}

interface SimAgentTurn {
  phase: string;
  thought: string;
  tool: string;
  result: string;
}

interface SubstitutionSimulation {
  simulation_id: string;
  branch_id: string;
  live_branch?: boolean;
  status: string;
  steps: { id: string; label: string; detail: string; duration_ms: number; status: string; transcript?: SimAgentTurn[] }[];
  live_transcript?: SimAgentTurn[];
  impact?: {
    shortage_item_id: string;
    shortage_item_description: string;
    alternative_item_id: string;
    alternative_item_description: string;
    patients_affected: number;
    allergy_flags: number;
    contraindications: number;
    monthly_cost_delta: number;
    naive_monthly_cost_delta?: number | null;
    alt_on_hand: number;
    forecast_demand_90d: number;
    covers_90d: boolean;
    delayed_facilities: string[];
    facilities: SimFacility[];
    summary: string;
    agent?: {
      planner?: string;
      transcript?: SimAgentTurn[];
      categories?: SimAgentCategory[];
      unexpected?: string[];
      report_markdown?: string;
      cost?: { monthly_cost_delta?: number | null; naive_monthly_cost_delta?: number | null; note?: string };
    };
  };
}

interface RecallItem {
  recall_id: number;
  fda_recall_number: string;
  recall_class: string;
  item_id: string;
  item_description: string;
  affected_lot: string;
  facility_id: string;
  facility_name: string;
  location_in_facility: string;
  qty_on_hand: number;
  patient_exposure_count: number;
  recall_date: string;
  status: string;
}

interface TransferItem {
  transfer_id: number;
  item_id: string;
  item_description: string;
  from_facility_name: string;
  to_facility_name: string;
  recommended_qty: number;
  reason: string;
  from_days_of_supply: number;
  to_days_of_supply: number;
  status: string;
}

interface BranchRole {
  id: string;
  identity: string;
  identity_type: string;
  purpose?: string;
  branch_id?: string;
}

interface Branch {
  id: string;
  state: string;
  default: boolean;
  parent?: string | null;
  logical_size_bytes?: number;
  ttl_seconds?: number;
  roles?: BranchRole[];
  connection?: {
    host: string;
    port: number;
    database: string;
    schema: string;
    connection_string: string;
  };
}

type RiskLevel = "high" | "medium" | "low";

const wholeNumber = (v: unknown, fallback = 0) => {
  const n = Number(v);
  return Math.round(Number.isFinite(n) ? n : fallback);
};

const RISK_FACTOR_META: Record<string, { label: string; format: (v: any) => string; level?: (v: any) => RiskLevel; meter?: (v: any) => number }> = {
  supplier_reliability: {
    label: "Supplier reliability",
    format: (v) => `${Math.round(Number(v) * 100)}%`,
    level: (v) => (v < 0.5 ? "high" : v < 0.75 ? "medium" : "low"),
    meter: (v) => Number(v),
  },
  lead_time_variance_days: {
    label: "Lead time variance",
    format: (v) => `±${wholeNumber(v)} days`,
    level: (v) => (v >= 14 ? "high" : v >= 7 ? "medium" : "low"),
    meter: (v) => Math.min(Number(v) / 21, 1),
  },
  port_congestion_index: {
    label: "Port congestion",
    format: (v) => `${Math.round(Number(v) * 100)} / 100`,
    level: (v) => (v >= 0.75 ? "high" : v >= 0.5 ? "medium" : "low"),
    meter: (v) => Number(v),
  },
  formulary_spike: {
    label: "Demand driver",
    format: (v) => String(v),
  },
};

const humanizeKey = (key: string) =>
  key.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());

function RiskFactorList({ factors }: { factors: Record<string, any> | string }) {
  let parsed: Record<string, any> = {};
  if (typeof factors === "string") {
    try {
      parsed = JSON.parse(factors);
    } catch {
      parsed = { details: factors };
    }
  } else if (factors) {
    parsed = factors;
  }
  const entries = Object.entries(parsed);
  if (entries.length === 0) {
    return <p className="risk-factor-empty">No risk factors recorded.</p>;
  }
  return (
    <ul className="risk-factor-list">
      {entries.map(([key, value]) => {
        const meta = RISK_FACTOR_META[key];
        const numeric = typeof value === "number";
        const level = meta?.level && numeric ? meta.level(value) : undefined;
        const meter = meta?.meter && numeric ? meta.meter(value) : undefined;
        const display = meta ? meta.format(value) : typeof value === "object" ? JSON.stringify(value) : String(value);
        return (
          <li key={key} className="risk-factor-row">
            <div className="risk-factor-head">
              <span className="risk-factor-label">{meta?.label ?? humanizeKey(key)}</span>
              <span className={`risk-factor-value${level ? ` risk-${level}` : ""}`}>{display}</span>
            </div>
            {meter !== undefined && (
              <div className="risk-factor-meter">
                <div className={`risk-factor-meter-fill risk-bg-${level}`} style={{ width: `${Math.round(meter * 100)}%` }} />
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function ArchitectureFlow({
  flow,
  selected,
  onSelect,
  onSimulate,
  simulating,
}: {
  flow: any;
  selected: string;
  onSelect: (id: string) => void;
  onSimulate: () => void;
  simulating: boolean;
}) {
  const stages = [
    {
      id: "planning",
      icon: Database,
      title: "Planning & Forecasting",
      copy: "Governed ERP, EHR, pharmacy, and distributor data supports demand forecasts and procurement recommendations.",
    },
    {
      id: "serving",
      icon: Zap,
      title: "Operational Decision Services",
      copy: "API-ready views and transactional workflows support fast, reliable decisions across every facility.",
    },
    {
      id: "feedback",
      icon: Activity,
      title: "Performance & Planning Feedback",
      copy: "Materials decisions, substitutions, and recall closures improve reporting, future forecasts, and planning guidance.",
    },
  ];
  const meta = flow?.stages || {};
  const edges = flow?.edges || [];
  return (
    <div>
      <div className="ltap-diagram">
        {stages.map((stage, idx) => {
          const info = meta[stage.id] || {};
          const Icon = stage.icon;
          const edge = idx > 0 ? edges[idx - 1] : null;
          const decisionHealthy = (flow?.lakebase_to_delta_cdf || []).some(
            (row: any) => row.status === "Streaming" || row.status === "Snapshotting"
          );
          const edgeHealthy = idx === 2
            ? (info.status === "healthy" || decisionHealthy)
            : edge
              ? edge.healthy !== false
              : info.status !== "issue";
          const status = info.status || "healthy";
          return (
            <React.Fragment key={stage.id}>
              {idx > 0 && (
                <button
                  type="button"
                  className={`ltap-arrow ${selected === edge?.from ? "active" : ""} ${edgeHealthy ? "flow-healthy" : "flow-issue"}`}
                  onClick={() => onSelect(edge?.from || stage.id)}
                >
                  <span className="ltap-flow-dir">
                    <ChevronRight size={22} />
                    <ChevronRight size={22} />
                  </span>
                  <span>{idx === 1 ? "Data products" : "Decision Events"}</span>
                </button>
              )}
              <button
                type="button"
                className={`ltap-block ${stage.id === "serving" ? "highlight" : ""} ${selected === stage.id ? "selected" : ""} ${status === "issue" ? "flow-issue" : "flow-healthy"}`}
                onClick={() => onSelect(stage.id)}
              >
                <span className="ltap-block-inner">
                  <span className="ltap-block-head">
                    <Icon size={18} color={status === "issue" ? "#dc2626" : "#087c91"} />
                    <strong>{stage.title}</strong>
                    <span className={`badge ${status === "healthy" ? "ready" : "critical"}`}>{status === "issue" ? "Issue" : "Healthy"}</span>
                  </span>
                  <p>{stage.copy}</p>
                  <span className="ltap-block-metrics">
                    <span>{Number(info.records || 0).toLocaleString()} records</span>
                    <span>{info.detail || "Waiting for telemetry"}</span>
                  </span>
                  {stage.id === "planning" ? (
                    <span
                      className="btn btn-secondary btn-sm ltap-block-action"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSimulate();
                      }}
                    >
                      <Boxes size={12} /> {simulating ? "Simulating…" : "Simulate inventory feed"}
                    </span>
                  ) : (
                    <span className="ltap-block-action ltap-block-action-spacer" aria-hidden="true" />
                  )}
                </span>
              </button>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

function InsightBars({ rows }: { rows: { label: string; count: number }[] }) {
  const max = Math.max(...rows.map((row) => row.count), 1);
  if (rows.length === 0) {
    return <p className="insight-empty">No events yet.</p>;
  }
  return (
    <ul className="insight-bars">
      {rows.map((row) => (
        <li key={row.label}>
          <span className="insight-bar-label" title={row.label}>{row.label}</span>
          <span className="insight-bar-track">
            <span style={{ width: `${Math.max((row.count / max) * 100, 4)}%` }} />
          </span>
          <strong>{row.count}</strong>
        </li>
      ))}
    </ul>
  );
}

function branchTypeLabel(branch: Branch): string {
  if (branch.default || branch.id === "production") return "Production";
  if (branch.id.startsWith("sim-")) return "Agent Branch";
  return "Feature branch";
}

function BranchTree({ branches, highlightId }: { branches: Branch[]; highlightId?: string }) {
  const byParent = new Map<string, Branch[]>();
  const ids = new Set(branches.map((b) => b.id));
  const roots: Branch[] = [];
  for (const branch of branches) {
    const parent = branch.parent || (branch.default || branch.id === "production" ? null : "production");
    if (!parent || !ids.has(parent)) {
      roots.push(branch);
    } else {
      const kids = byParent.get(parent) || [];
      kids.push(branch);
      byParent.set(parent, kids);
    }
  }
  roots.sort((a, b) => Number(!!b.default) - Number(!!a.default) || a.id.localeCompare(b.id));
  const render = (branch: Branch) => (
    <li key={branch.id}>
      <div className={`branch-tree-node ${branch.default ? "primary" : ""} ${branch.id === highlightId ? "current" : ""}`}>
        <GitBranch size={14} />
        <strong>{branch.id}</strong>
        {branch.default && <span className="badge ready">Parent</span>}
      </div>
      {(byParent.get(branch.id) || []).length > 0 && (
        <ul>{(byParent.get(branch.id) || []).map(render)}</ul>
      )}
    </li>
  );
  if (branches.length === 0) {
    return <p className="ltap-hint">No environments loaded yet.</p>;
  }
  return (
    <div className="branch-tree">
      <ul>{roots.map(render)}</ul>
    </div>
  );
}

type WorkspacePersona = "materials" | "pharmacist";

const PERSONA_HOME: Record<WorkspacePersona, string> = {
  materials: "risk-command",
  pharmacist: "substitutions",
};

const PERSONA_TABS: Record<WorkspacePersona, string[]> = {
  materials: ["risk-command", "orders", "transfers"],
  pharmacist: ["substitutions", "recalls"],
};

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("risk-command");
  const [persona, setPersona] = useState<WorkspacePersona>("materials");
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [riskItems, setRiskItems] = useState<RiskItem[]>([]);
  const [orders, setOrders] = useState<RecommendedOrder[]>([]);
  const [substitutions, setSubstitutions] = useState<SubstitutionCandidate[]>([]);
  const [recalls, setRecalls] = useState<RecallItem[]>([]);
  const [transfers, setTransfers] = useState<TransferItem[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [migrations, setMigrations] = useState<any[]>([]);
  const [health, setHealth] = useState<any>({ latency_ms: 3.4, database: "lakebase_autoscaling" });
  const [compute, setCompute] = useState<any>({
    current_cu: null,
    min_cu: 1,
    max_cu: 1,
    approx_ram_gb: 2,
    connections: 0,
    active_queries: 0,
    idle_connections: 0,
    transactions_committed: 0,
    tuples_fetched: 0,
    state: null,
    observed_at: null,
  });
  const [flowStatus, setFlowStatus] = useState<any>(null);
  const [selectedStage, setSelectedStage] = useState<string>("serving");
  const [simulating, setSimulating] = useState<boolean>(false);
  const [similarByItem, setSimilarByItem] = useState<Record<string, { loading: boolean; matches: any[] }>>({});
  const [expandedShortageId, setExpandedShortageId] = useState<string | null>(null);

  // Filters
  const [riskFilter, setRiskFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Modals & Active Selections
  const [selectedRiskItem, setSelectedRiskItem] = useState<RiskItem | null>(null);
  const [modifyOrderModal, setModifyOrderModal] = useState<RecommendedOrder | null>(null);
  const [modifyQty, setModifyQty] = useState<number>(0);
  const [modifySupplier, setModifySupplier] = useState<string>("");
  const [rejectOrderModal, setRejectOrderModal] = useState<RecommendedOrder | null>(null);
  const [rejectReason, setRejectReason] = useState<string>("");
  
  // Substitution Selection
  const [selectSubModal, setSelectSubModal] = useState<SubstitutionCandidate | null>(null);
  const [clinicalNotes, setClinicalNotes] = useState<string>("");
  const [simSource, setSimSource] = useState<SubstitutionCandidate | null>(null);
  const [simulation, setSimulation] = useState<SubstitutionSimulation | null>(null);
  const [simError, setSimError] = useState<string>("");
  const [simFacilityIds, setSimFacilityIds] = useState<string[]>([]);

  // AI Agent Chat State
  const [agentPrompt, setAgentPrompt] = useState<string>("");
  const [agentResponse, setAgentResponse] = useState<string>("");
  const [agentLoading, setAgentLoading] = useState<boolean>(false);

  // Platform Admin Modals
  const [createBranchModal, setCreateBranchModal] = useState<boolean>(false);
  const [newBranchId, setNewBranchId] = useState<string>("");
  const [newBranchTTL, setNewBranchTTL] = useState<number>(86400);
  const [branchParent, setBranchParent] = useState<string>("production");
  const [credentialModal, setCredentialModal] = useState<any | null>(null);
  const [roleModal, setRoleModal] = useState<string | null>(null);
  const [roleIdentity, setRoleIdentity] = useState<string>("");
  const [roleType, setRoleType] = useState<string>("USER");
  const [rolePermission, setRolePermission] = useState<string>("CAN_CONNECT_AND_CREATE");
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date | null>(null);
  const [tracedRecallId, setTracedRecallId] = useState<number | null>(null);
  const [decisionInsights, setDecisionInsights] = useState<any>(null);
  const [commentDrafts, setCommentDrafts] = useState<Record<number, string>>({});
  const [savingCommentId, setSavingCommentId] = useState<number | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const fetchData = async (manual = false) => {
    if (manual) setIsRefreshing(true);
    const refreshSuffix = manual ? `?refresh=${Date.now()}` : "";

    try {
      const noStore = { cache: "no-store" as RequestCache };
      const [hRes, dRes, rRes, oRes, sRes, rcRes, tRes, bRes, mRes, cRes, fRes, iRes] = await Promise.all([
        fetch(`/api/health${refreshSuffix}`, noStore).then((r) => r.json()).catch(() => ({ latency_ms: 2.1, database: "lakebase" })),
        fetch(`/api/dashboard${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => ({ kpis: [] })),
        fetch(`/api/risk-scores${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/recommended-orders${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/substitutions${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/recalls${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/transfers${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/platform/branches${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/platform/branches/production/migrations${refreshSuffix}`, { cache: manual ? "no-store" : "default" }).then((r) => r.json()).catch(() => []),
        fetch(`/api/platform/compute${refreshSuffix}`, noStore).then((r) => r.json()).catch(() => null),
        fetch(`/api/ltap-status${refreshSuffix}`, noStore).then((r) => (r.ok ? r.json() : null)).catch(() => null),
        fetch(`/api/decision-insights${refreshSuffix}`, noStore).then((r) => (r.ok ? r.json() : null)).catch(() => null),
      ]);

      setHealth(hRes);
      if (cRes && typeof cRes === "object" && cRes.observed_at) setCompute(cRes);
      if (fRes && Array.isArray(fRes.synced_tables)) setFlowStatus(fRes);
      if (iRes && iRes.kpis) setDecisionInsights(iRes);
      if (dRes.kpis) setKpis(dRes.kpis);
      if (Array.isArray(rRes)) setRiskItems(rRes);
      if (Array.isArray(oRes)) {
        setOrders(oRes);
        setCommentDrafts((prev) => {
          const next = { ...prev };
          for (const order of oRes as RecommendedOrder[]) {
            if (next[order.recommendation_id] === undefined) {
              next[order.recommendation_id] = order.comments || "";
            }
          }
          return next;
        });
      }
      if (Array.isArray(sRes)) setSubstitutions(sRes);
      if (Array.isArray(rcRes)) setRecalls(rcRes);
      if (Array.isArray(tRes)) setTransfers(tRes);
      if (Array.isArray(bRes)) setBranches(bRes);
      if (Array.isArray(mRes)) setMigrations(mRes);
      const refreshedAt = new Date();
      setLastRefreshedAt(refreshedAt);
      if (manual) {
        showToast(`Supply feed refreshed at ${refreshedAt.toLocaleTimeString()}`);
      }
    } catch (err) {
      console.error("Data fetch error", err);
      if (manual) showToast("Unable to refresh the supply feed");
    } finally {
      if (manual) setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === "ltap-flow") setActiveTab("platform-admin");
  }, [activeTab]);

  useEffect(() => {
    if (!simulating && !simulation) return;
    document.getElementById("shortage-alt-sim")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [simulating, simulation?.simulation_id]);

  // Order Decisions
  const handleSaveOrderComment = async (orderId: number) => {
    const comments = (commentDrafts[orderId] ?? "").trim();
    setSavingCommentId(orderId);
    try {
      const res = await fetch(`/api/recommended-orders/${orderId}/comments`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comments }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data.detail;
        const message = Array.isArray(detail)
          ? detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join("; ")
          : detail;
        throw new Error(message || `Could not save comment (${res.status})`);
      }
      setOrders((prev) =>
        prev.map((order) => (order.recommendation_id === orderId ? { ...order, comments } : order))
      );
      setCommentDrafts((prev) => ({ ...prev, [orderId]: comments }));
      showToast("Comment saved on the purchase order");
    } catch (err: any) {
      showToast(err?.message || "Unable to save comment");
    } finally {
      setSavingCommentId(null);
    }
  };

  const handleApproveOrder = async (orderId: number) => {
    try {
      await fetch(`/api/recommended-orders/${orderId}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recommendation_id: orderId, decision: "approved" }),
      });
      setOrders((prev) =>
        prev.map((o) => (o.recommendation_id === orderId ? { ...o, decision_status: "approved" } : o))
      );
      showToast(`Recommended Order PO-${orderId} Approved and Queued for Dispatch`);
    } catch (err) {
      showToast("Error approving order");
    }
  };

  const handleModifyOrder = async () => {
    if (!modifyOrderModal) return;
    try {
      await fetch(`/api/recommended-orders/${modifyOrderModal.recommendation_id}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recommendation_id: modifyOrderModal.recommendation_id,
          decision: "modified",
          modified_qty: modifyQty,
          modified_supplier_id: modifySupplier,
          decision_reason: "Materials manager adjusted volume for surge buffer",
        }),
      });
      setOrders((prev) =>
        prev.map((o) =>
          o.recommendation_id === modifyOrderModal.recommendation_id
            ? { ...o, decision_status: "modified", recommended_qty: modifyQty, total_cost: modifyQty * o.unit_cost }
            : o
        )
      );
      showToast(`Order PO-${modifyOrderModal.recommendation_id} Modified & Saved`);
      setModifyOrderModal(null);
    } catch (err) {
      showToast("Error modifying order");
    }
  };

  const handleRejectOrder = async () => {
    if (!rejectOrderModal) return;
    try {
      await fetch(`/api/recommended-orders/${rejectOrderModal.recommendation_id}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recommendation_id: rejectOrderModal.recommendation_id,
          decision: "rejected",
          decision_reason: rejectReason || "Rejected by clinician due to local safety buffer",
        }),
      });
      setOrders((prev) =>
        prev.map((o) => (o.recommendation_id === rejectOrderModal.recommendation_id ? { ...o, decision_status: "rejected" } : o))
      );
      showToast(`Order PO-${rejectOrderModal.recommendation_id} Rejected`);
      setRejectOrderModal(null);
    } catch (err) {
      showToast("Error rejecting order");
    }
  };

  // Substitution Selection
  const handleSelectSub = async () => {
    if (!selectSubModal) return;
    try {
      await fetch("/api/substitutions/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          substitution_id: selectSubModal.substitution_id,
          shortage_item_id: selectSubModal.shortage_item_id,
          selected_alternative_id: selectSubModal.alternative_item_id,
          clinical_notes: clinicalNotes || "Clinical equivalence verified by staff pharmacist.",
        }),
      });
      showToast(`Clinical Alternative ${selectSubModal.alternative_item_id} Approved`);
      setSelectSubModal(null);
      setClinicalNotes("");
    } catch (err) {
      showToast("Error recording substitution");
    }
  };

  const handleSimulateSubstitution = async (
    sub: SubstitutionCandidate,
    branchId?: string,
    facilityIds?: string[],
    prompt?: string
  ) => {
    setSimSource(sub.substitution_id ? sub : null);
    setSimulating(true);
    setSimError("");
    setSimulation({
      simulation_id: "",
      branch_id: branchId || "",
      status: "running",
      steps: [{ id: "branch", label: "Isolate", detail: "Creating working copy from production", duration_ms: 0, status: "running" }],
    });
    try {
      const res = await fetch("/api/substitutions/simulate?stream=1", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/x-ndjson" },
        body: JSON.stringify({
          substitution_id: sub.substitution_id,
          shortage_item_id: sub.shortage_item_id,
          alternative_item_id: sub.alternative_item_id,
          shortage_item_description: sub.shortage_item_description,
          alternative_item_description: sub.alternative_item_description,
          branch_id: branchId,
          facility_ids: facilityIds,
          prompt,
        }),
      });
      if (!res.ok || !res.body) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Simulation failed (${res.status})`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let finalPayload: SubstitutionSimulation | null = null;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.trim()) continue;
          const event = JSON.parse(line);
          if (event.event === "step") {
            const running = (event.steps || []).find((step: { status?: string; transcript?: SimAgentTurn[] }) => step.status === "running")
              || (event.steps || []).find((step: { transcript?: SimAgentTurn[] }) => step.transcript);
            setSimulation((prev) => ({
              simulation_id: prev?.simulation_id || "",
              branch_id: event.branch_id || prev?.branch_id || "",
              status: "running",
              steps: event.steps || prev?.steps || [],
              live_transcript: running?.transcript || prev?.live_transcript,
              impact: prev?.impact,
            }));
          } else if (event.event === "complete") {
            finalPayload = event.simulation;
            setSimulation(event.simulation);
          } else if (event.event === "error") {
            throw new Error(event.detail || "Simulation failed");
          }
        }
      }
      if (buffer.trim()) {
        const event = JSON.parse(buffer);
        if (event.event === "complete") {
          finalPayload = event.simulation;
          setSimulation(event.simulation);
        } else if (event.event === "error") {
          throw new Error(event.detail || "Simulation failed");
        }
      }
      const data = finalPayload;
      if (!data?.impact) {
        throw new Error("Simulation did not complete");
      }
      setSimFacilityIds((data.impact.facilities || []).map((f: SimFacility) => f.facility_id));
      showToast(`Impact simulation ready for ${data.impact.shortage_item_description || sub.shortage_item_description}`);
    } catch (err: any) {
      setSimError(err?.message || "Unable to simulate shortage impact");
      showToast("Substitution simulation failed");
    } finally {
      setSimulating(false);
    }
  };

  const handleSimDecision = async (decision: "approved" | "rejected" | "modified") => {
    if (!simulation) return;
    setSimulating(true);
    setSimError("");
    try {
      const res = await fetch(`/api/substitutions/simulate/${simulation.simulation_id}/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          facility_ids: decision === "modified" ? simFacilityIds : undefined,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || `Decision failed (${res.status})`);
      }
      if (decision === "rejected") {
        setSimulation(null);
        setSimSource(null);
        showToast("Simulation discarded. Live formulary is unchanged.");
        fetchData();
        return;
      }
      if (decision === "modified") {
        setSimulation(data);
        setSimFacilityIds((data.impact?.facilities || []).map((f: SimFacility) => f.facility_id));
        showToast(`Same branch ${data.branch_id} re-simulated with the selected facilities.`);
        return;
      }
      setSimulation({ ...simulation, status: "approved", impact: data.impact || simulation.impact });
      showToast("Plan approved. Apply it to the live formulary when ready.");
    } catch (err: any) {
      setSimError(err?.message || "Unable to apply the simulation decision");
    } finally {
      setSimulating(false);
    }
  };

  const handleReplayToProduction = async () => {
    if (!simulation || simulation.status !== "approved") return;
    setSimulating(true);
    setSimError("");
    try {
      const res = await fetch(`/api/substitutions/simulate/${simulation.simulation_id}/replay`, {
        method: "POST",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || `Could not apply to live formulary (${res.status})`);
      }
      setSimulation({ ...simulation, status: "shipped", impact: data.impact || simulation.impact });
      showToast("Approved substitution applied to the live formulary.");
      fetchData();
    } catch (err: any) {
      setSimError(err?.message || "Unable to apply the approved plan to the live formulary");
    } finally {
      setSimulating(false);
    }
  };

  const focusPharmacistAdvisor = () => {
    document.getElementById("pharmacist-advisor")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  // AI Agent Query
  const handleAgentQuery = async (customPrompt?: string) => {
    const q = (customPrompt || agentPrompt).trim();
    if (!q) return;
    if (customPrompt) setAgentPrompt(q);
    focusPharmacistAdvisor();
    const wantsSimulation = /simulate\s+(switching|impact|substitution)/i.test(q) || (/simulate/i.test(q) && /switch/i.test(q));
    if (wantsSimulation) {
      const fromLisinopril = /lisinopril/i.test(q);
      const fromCefazolin = /cefazolin/i.test(q);
      const target =
        substitutions.find((s) => fromLisinopril && s.shortage_item_id === "SKU-PH-112") ||
        substitutions.find((s) => fromCefazolin && s.shortage_item_id === "SKU-PH-101" && s.alternative_item_id === "SKU-PH-ALT-02") ||
        substitutions[0];
      const fallback: SubstitutionCandidate = {
        substitution_id: 0,
        shortage_item_id: "",
        shortage_item_description: "",
        alternative_item_id: "",
        alternative_item_description: "",
        clinical_equivalence: "",
        formulary_status: "",
        availability: "",
        agent_reasoning: "",
        confidence_score: 0,
      };
      await handleSimulateSubstitution(target || fallback, undefined, undefined, q);
      return;
    }
    setAgentLoading(true);
    setAgentResponse("");
    try {
      const res = await fetch("/api/substitutions/agent-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: q,
          item_id: selectedRiskItem ? selectedRiskItem.item_id : "General Formulary",
        }),
      }).then((r) => r.json());
      setAgentResponse(res.response);
    } catch (err) {
      setAgentResponse("Clinical guidance is temporarily unavailable. Please review the formulary alternatives below.");
    } finally {
      setAgentLoading(false);
    }
  };

  const loadCatalogMatches = async (itemId: string, query: string) => {
    setSimilarByItem((prev) => ({
      ...prev,
      [itemId]: { loading: true, matches: prev[itemId]?.matches || [] },
    }));
    try {
      const params = new URLSearchParams();
      if (query) params.set("q", query);
      params.set("item_id", itemId);
      params.set("limit", "4");
      const response = await fetch(`/api/catalog/similar?${params.toString()}`, { cache: "no-store" });
      const res = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(res.detail || `Catalog search failed (${response.status})`);
      }
      setSimilarByItem((prev) => ({
        ...prev,
        [itemId]: { loading: false, matches: res.matches || [] },
      }));
    } catch (err) {
      setSimilarByItem((prev) => ({
        ...prev,
        [itemId]: { loading: false, matches: prev[itemId]?.matches || [] },
      }));
      showToast(err instanceof Error ? err.message : "Additional catalog matches are unavailable");
    }
  };

  const openShortageAlternatives = (itemId: string, description: string) => {
    setExpandedShortageId(itemId);
    if (!similarByItem[itemId]?.matches?.length) {
      void loadCatalogMatches(itemId, description);
    }
  };

  const handleSimulateInventory = async () => {
    setSimulating(true);
    try {
      const response = await fetch("/api/simulate/inventory", { method: "POST" });
      const res = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(res.detail || `Inventory simulation failed (${response.status})`);
      }
      const count = Array.isArray(res.updated) ? res.updated.length : 0;
      showToast(`Inventory feed simulated for ${count} SKUs. Shortage days of supply were recalculated.`);
      await fetchData(true);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Inventory simulation failed");
    } finally {
      setSimulating(false);
    }
  };

  // Recall Action
  const handleRecallAction = async (recallId: number, actionType: string) => {
    try {
      if (actionType === "traced_patients" && tracedRecallId === recallId) {
        setTracedRecallId(null);
        return;
      }
      await fetch(`/api/recalls/${recallId}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recall_id: recallId, action_type: actionType, notes: "Verified lot isolated." }),
      });
      if (actionType === "traced_patients") {
        setTracedRecallId(recallId);
        showToast(`Patient exposure roster opened for recall #${recallId}. A recall_actions CDF event was written.`);
        await fetchData();
        return;
      }
      setRecalls((prev) =>
        prev.map((r) => (r.recall_id === recallId ? { ...r, status: actionType === "quarantined" ? "quarantined" : r.status } : r))
      );
      showToast(`FDA Recall #${recallId}: '${actionType}' recorded and streamed as a Lakebase CDF event`);
      await fetchData();
    } catch (err) {
      showToast("Error submitting recall action");
    }
  };

  // Transfer Action
  const handleTransferConfirm = async (transferId: number, decision: string) => {
    try {
      await fetch(`/api/transfers/${transferId}/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transfer_id: transferId, decision, actual_qty: 50, notes: "Approved for inter-facility van transport" }),
      });
      setTransfers((prev) =>
        prev.map((t) => (t.transfer_id === transferId ? { ...t, status: decision } : t))
      );
      showToast(`Inter-Facility Transfer #${transferId}: ${decision.toUpperCase()}`);
    } catch (err) {
      showToast("Error confirming transfer");
    }
  };

  // Platform Admin Branch Actions
  const handleCreateBranch = async () => {
    if (!newBranchId) return;
    try {
      const res = await fetch("/api/platform/branches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          branch_id: newBranchId.toLowerCase().replace(/[^a-z0-9-]/g, "-"),
          parent: branchParent || "production",
          ttl_seconds: newBranchTTL,
        }),
      }).then((r) => r.json());
      setBranches((prev) => [...prev, res]);
      showToast(`Isolated database environment '${res.id}' created successfully.`);
      setCreateBranchModal(false);
      setNewBranchId("");
    } catch (err) {
      showToast("Failed to create database environment");
    }
  };

  const handleDeleteBranch = async (branchId: string) => {
    if (branchId === "production") return;
    if (!confirm(`Delete database environment '${branchId}'? Its isolated data and schema changes will be removed.`)) return;
    try {
      await fetch(`/api/platform/branches/${branchId}`, { method: "DELETE" });
      setBranches((prev) => prev.filter((b) => b.id !== branchId));
      showToast(`Database environment '${branchId}' deleted.`);
    } catch (err) {
      showToast("Failed to delete database environment");
    }
  };

  const handleGenerateCred = async (branchId: string) => {
    try {
      const res = await fetch(`/api/platform/branches/${branchId}/credential`, { method: "POST" }).then((r) => r.json());
      setCredentialModal(res);
    } catch (err) {
      showToast("Failed to generate credential");
    }
  };

  const handleAssignRole = async () => {
    if (!roleModal || !roleIdentity) return;
    try {
      await fetch(`/api/platform/branches/${roleModal}/roles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          branch_id: roleModal,
          identity: roleIdentity,
          role_type: roleType,
          permission: rolePermission,
        }),
      });
      showToast(`Role granted to ${roleIdentity} in environment '${roleModal}'.`);
      setRoleModal(null);
      setRoleIdentity("");
    } catch (err) {
      showToast("Failed to assign role");
    }
  };

  // Filtered Risk Items
  const filteredRiskItems = riskItems.filter((item) => {
    const matchesTier = riskFilter === "all" || item.risk_tier === riskFilter;
    const matchesCategory = categoryFilter === "all" || item.item_category.toLowerCase() === categoryFilter.toLowerCase();
    const matchesSearch =
      !searchQuery ||
      item.item_description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.item_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTier && matchesCategory && matchesSearch;
  });

  const uniqueBy = <T,>(rows: T[], keyFn: (row: T) => string): T[] => {
    const seen = new Set<string>();
    return rows.filter((row) => {
      const key = keyFn(row);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  };

  const uniqueOrders = uniqueBy(orders, (o) => `${o.item_id}-${o.facility_id}`);
  const uniqueSubstitutions = uniqueBy(substitutions, (s) => `${s.shortage_item_id}-${s.alternative_item_id}`);
  const shortageGroups = Array.from(
    uniqueSubstitutions.reduce((groups, sub) => {
      const rows = groups.get(sub.shortage_item_id) || [];
      rows.push(sub);
      groups.set(sub.shortage_item_id, rows);
      return groups;
    }, new Map<string, SubstitutionCandidate[]>())
  );
  const uniqueRecalls = uniqueBy(recalls, (r) => `${r.fda_recall_number}-${r.affected_lot}-${r.facility_id}`);
  const uniqueTransfers = uniqueBy(transfers, (t) => `${t.item_id}-${t.from_facility_name}-${t.to_facility_name}`);

  const exposurePatients = (recall: RecallItem) =>
    Array.from({ length: Math.max(recall.patient_exposure_count, 0) }, (_, index) => ({
      mrn: `MRN-${recall.facility_id}-${String(10000 + recall.recall_id * 50 + index).padStart(6, "0")}`,
      encounter: `ENC-2026-${recall.recall_id}-${index + 1}`,
      unit: recall.location_in_facility,
    }));

  const isSupplyOperation = [
    "risk-command",
    "orders",
    "substitutions",
    "recalls",
    "transfers",
    "decision-insights",
  ].includes(activeTab);

  const switchPersona = (next: WorkspacePersona) => {
    setPersona(next);
    const home = PERSONA_HOME[next];
    const primary = PERSONA_TABS[next];
    if (!primary.includes(activeTab) && activeTab !== "decision-insights" && activeTab !== "platform-admin") {
      setActiveTab(home);
    }
  };

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          backgroundColor: "#0f172a",
          color: "#ffffff",
          padding: "12px 20px",
          borderRadius: "10px",
          boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
          zIndex: 100,
          display: "flex",
          alignItems: "center",
          gap: "10px",
          fontSize: "13px",
          fontWeight: 600,
          border: "1px solid #334155"
        }}>
          <CheckCircle2 size={18} color="#10b981" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* SIDEBAR NAVIGATION */}
      <aside className="sidebar">
        <div className="brand-section">
          <div className="brand-icon">
            <Boxes size={22} />
          </div>
          <div className="brand-info">
            <h2>Apex Healthcare</h2>
            <span>Supply Intelligence</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className={`nav-group ${persona === "materials" ? "nav-group-active" : ""}`}>
            <div className="nav-section-title">Supply operations</div>
            <button
              className={`nav-button ${activeTab === "risk-command" ? "active" : ""}`}
              onClick={() => {
                setPersona("materials");
                setActiveTab("risk-command");
              }}
            >
              <AlertTriangle size={17} />
              <span>Risk Command Center</span>
              <span className="nav-badge alert">30</span>
            </button>
            <button
              className={`nav-button ${activeTab === "orders" ? "active" : ""}`}
              onClick={() => {
                setPersona("materials");
                setActiveTab("orders");
              }}
            >
              <FileText size={17} />
              <span>Recommended Orders</span>
              <span className="nav-badge">100</span>
            </button>
            <button
              className={`nav-button ${activeTab === "transfers" ? "active" : ""}`}
              onClick={() => {
                setPersona("materials");
                setActiveTab("transfers");
              }}
            >
              <ArrowRightLeft size={17} />
              <span>Inter-Facility Transfers</span>
              <span className="nav-badge">20</span>
            </button>
          </div>

          <div className={`nav-group ${persona === "pharmacist" ? "nav-group-active" : ""}`}>
            <div className="nav-section-title">Pharmacy operations</div>
            <button
              className={`nav-button ${activeTab === "substitutions" ? "active" : ""}`}
              onClick={() => {
                setPersona("pharmacist");
                setActiveTab("substitutions");
              }}
            >
              <BrainCircuit size={17} />
              <span>Clinical Substitutions</span>
              <span className="nav-badge">15</span>
            </button>
            <button
              className={`nav-button ${activeTab === "recalls" ? "active" : ""}`}
              onClick={() => {
                setPersona("pharmacist");
                setActiveTab("recalls");
              }}
            >
              <ShieldAlert size={17} />
              <span>FDA Recall Response</span>
              <span className="nav-badge alert">3</span>
            </button>
          </div>

          <div className="nav-section-title">Shared</div>
          <button
            className={`nav-button ${activeTab === "decision-insights" ? "active" : ""}`}
            onClick={() => setActiveTab("decision-insights")}
          >
            <BarChart3 size={17} />
            <span>Decision Insights</span>
            <span className="nav-badge">{decisionInsights?.kpis?.[0]?.value ?? "CDF"}</span>
          </button>

          <div className="nav-section-title">Administration</div>
          <button
            className={`nav-button ${activeTab === "platform-admin" ? "active" : ""}`}
            onClick={() => setActiveTab("platform-admin")}
          >
            <GitBranch size={17} />
            <span>Platform Operations</span>
            <span className="nav-badge">{branches.length}</span>
          </button>
        </nav>
      </aside>

      {/* MAIN VIEWPORT */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-left">
            <div className="header-facility-pill">
              <Building2 size={15} color="#087c91" />
              <span>Apex Memorial Hospital & 7 Regional Facilities</span>
            </div>
          </div>

          <div className="header-right">
            <div className="persona-switch" role="group" aria-label="Workspace persona">
              <button
                type="button"
                className={`persona-chip ${persona === "materials" ? "active" : ""}`}
                onClick={() => switchPersona("materials")}
              >
                Materials manager
              </button>
              <button
                type="button"
                className={`persona-chip ${persona === "pharmacist" ? "active" : ""}`}
                onClick={() => switchPersona("pharmacist")}
              >
                Pharmacist
              </button>
            </div>
            <div className="live-metrics-chip">
              <Zap size={14} />
              <span>Live Supply Network</span>
            </div>
            <div className="user-profile-badge">
              <div className="avatar-circle">SG</div>
              <div className="user-profile-text">
                <strong>Sumanth Ghanta</strong>
                <small>{persona === "pharmacist" ? "Clinical pharmacist" : "Materials manager"}</small>
              </div>
            </div>
          </div>
        </header>

        {/* Content Tabs */}
        <main className={`page-container ${isSupplyOperation ? "operations-viewport" : ""} ${(activeTab === "substitutions" || activeTab === "decision-insights") ? "page-scrollable" : ""}`}>
          {activeTab === "risk-command" && (
            <div className="supply-operation-page">
              <div className="page-header">
                <div className="page-title-group">
                  <h1>Shortage Risk Command Center</h1>
                  <p>Predictive shortage signals combine inventory, demand, supplier, and clinical priorities across the Apex network.</p>
                </div>
                <div className="page-actions">
                  <div className="refresh-control">
                    <button
                      className="btn btn-secondary"
                      disabled={isRefreshing}
                      onClick={() => fetchData(true)}
                    >
                      <RefreshCw className={isRefreshing ? "spin" : ""} size={14} />
                      {isRefreshing ? "Refreshing..." : "Refresh Feed"}
                    </button>
                    <small aria-live="polite">
                      {lastRefreshedAt
                        ? `Updated ${lastRefreshedAt.toLocaleTimeString()}`
                        : "Waiting for first update"}
                    </small>
                  </div>
                  <button className="btn btn-primary" onClick={() => { setPersona("materials"); setActiveTab("orders"); }}>
                    Review Recommended Orders <ChevronRight size={14} />
                  </button>
                </div>
              </div>

              {/* KPI Cards Grid */}
              <div className="kpi-grid">
                {kpis.map((kpi, idx) => (
                  <div key={idx} className="kpi-card">
                    <div className="kpi-header">
                      <span className="kpi-label">{kpi.label}</span>
                      <div className={`kpi-icon ${kpi.status}`}>
                        {idx === 0 && <AlertTriangle size={18} />}
                        {idx === 1 && <Clock size={18} />}
                        {idx === 2 && <TrendingUp size={18} />}
                        {idx === 3 && <ShieldAlert size={18} />}
                      </div>
                    </div>
                    <div className="kpi-value">{kpi.value}</div>
                    <div className="kpi-subtext">{kpi.subtext}</div>
                    <div className={`kpi-trend ${kpi.status}`}>{kpi.trend}</div>
                  </div>
                ))}
              </div>

              {/* Shortage Risk Items Table Panel */}
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h3 className="panel-title">
                      <AlertTriangle size={18} color="#dc2626" />
                      Prioritized Shortage Exposure (30 Priority SKUs)
                    </h3>
                    <p className="panel-subtitle">Items ordered by predictive stockout risk score from the enterprise intelligence layer</p>
                  </div>
                  <span className="badge ready">Operational Data Live</span>
                </div>

                {/* Toolbar */}
                <div className="toolbar">
                  <div className="search-box">
                    <Search />
                    <input
                      type="text"
                      placeholder="Search medication, surgical device, SKU, or category..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>

                  <select
                    className="filter-select"
                    value={riskFilter}
                    onChange={(e) => setRiskFilter(e.target.value)}
                  >
                    <option value="all">All Risk Tiers</option>
                    <option value="critical">Critical Risk (&gt;85)</option>
                    <option value="high">High Risk (70-85)</option>
                    <option value="medium">Medium Risk (50-70)</option>
                    <option value="low">Low Risk (&lt;50)</option>
                  </select>

                  <select
                    className="filter-select"
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    <option value="all">All Categories</option>
                    <option value="pharmacy">Pharmacy</option>
                    <option value="surgical">Surgical Supplies</option>
                    <option value="critical care">Critical Care</option>
                    <option value="laboratory">Laboratory</option>
                    <option value="general medical">General Medical</option>
                  </select>
                </div>

                {/* Table */}
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Item & SKU</th>
                        <th>Category</th>
                        <th>On-Hand</th>
                        <th>Daily Burn</th>
                        <th>Days of Supply</th>
                        <th>Risk Score</th>
                        <th>30D Forecast</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredRiskItems.map((item) => (
                        <tr
                          key={item.item_id}
                          className="table-row-hover"
                          onClick={() => setSelectedRiskItem(item)}
                        >
                          <td>
                            <strong>{item.item_description}</strong>
                            <small style={{ color: "#64748b", display: "block" }}>{item.item_id}</small>
                          </td>
                          <td>
                            <span className="badge pending">{item.item_category}</span>
                          </td>
                          <td><strong>{item.current_on_hand}</strong> units</td>
                          <td>{item.avg_daily_usage} / day</td>
                          <td>
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                              <strong style={{ color: item.days_of_supply < 3 ? "#dc2626" : item.days_of_supply < 7 ? "#ea580c" : "#10b981" }}>
                                {wholeNumber(item.days_of_supply)}d
                              </strong>
                              <div style={{ width: "60px", height: "6px", backgroundColor: "#e2e8f0", borderRadius: "3px", overflow: "hidden" }}>
                                <div
                                  style={{
                                    width: `${Math.min(100, (item.days_of_supply / 15) * 100)}%`,
                                    height: "100%",
                                    backgroundColor: item.days_of_supply < 3 ? "#ef4444" : item.days_of_supply < 7 ? "#f97316" : "#10b981",
                                  }}
                                />
                              </div>
                            </div>
                          </td>
                          <td>
                            <span className={`badge ${item.risk_tier}`}>
                              {item.risk_score} - {item.risk_tier}
                            </span>
                          </td>
                          <td>
                            <strong>{item.forecast_demand_30d}</strong> units
                          </td>
                          <td>
                            <button
                              className="btn btn-secondary btn-sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedRiskItem(item);
                              }}
                            >
                              Inspect Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "orders" && (
            <div className="supply-operation-page">
              <div className="page-header">
                <div className="page-title-group">
                  <h1>Recommended Purchase Orders</h1>
                  <p>Procurement optimization recommendations combine demand forecasts, contract pricing, and supplier performance.</p>
                </div>
                <div className="page-actions">
                  <span className="live-metrics-chip">
                    <Database size={14} /> Published from Enterprise Analytics
                  </span>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h3 className="panel-title">
                      <FileText size={18} color="#087c91" />
                      Purchase Order Proposals ({uniqueOrders.length} unique SKU / facility)
                    </h3>
                    <p className="panel-subtitle">One-click decisions update operational workflows and feed downstream analytics</p>
                  </div>
                </div>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>PO Item & Facility</th>
                        <th>Recommended Supplier</th>
                        <th>Order Qty</th>
                        <th>Total Cost</th>
                        <th>Urgency</th>
                        <th>Recommendation Confidence</th>
                        <th>Status</th>
                        <th>Comments</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {uniqueOrders.map((order) => (
                        <tr key={order.recommendation_id}>
                          <td>
                            <strong>{order.item_description}</strong>
                            <small style={{ color: "#64748b", display: "block" }}>
                              {order.facility_name} ({order.item_id})
                            </small>
                          </td>
                          <td>
                            <strong>{order.supplier_name}</strong>
                            <small style={{ color: "#64748b", display: "block" }}>{order.supplier_id}</small>
                          </td>
                          <td><strong>{order.recommended_qty}</strong></td>
                          <td>${order.total_cost.toLocaleString()}</td>
                          <td>
                            <span className={`badge ${order.urgency}`}>
                              {order.urgency}
                            </span>
                          </td>
                          <td>{order.confidence_score}%</td>
                          <td>
                            <span className={`badge ${order.decision_status || order.decision || "pending"}`}>
                              {order.decision_status || order.decision || "pending"}
                            </span>
                          </td>
                          <td>
                            <div className="order-comment">
                              <textarea
                                className="form-control order-comment-input"
                                rows={2}
                                placeholder="Add a comment"
                                value={commentDrafts[order.recommendation_id] ?? order.comments ?? ""}
                                onChange={(e) =>
                                  setCommentDrafts((prev) => ({
                                    ...prev,
                                    [order.recommendation_id]: e.target.value,
                                  }))
                                }
                              />
                              <button
                                className="btn btn-secondary btn-sm"
                                disabled={savingCommentId === order.recommendation_id}
                                onClick={() => handleSaveOrderComment(order.recommendation_id)}
                              >
                                {savingCommentId === order.recommendation_id ? "Saving…" : "Save"}
                              </button>
                            </div>
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: "6px" }}>
                              <button
                                className="btn btn-success btn-sm"
                                disabled={order.decision_status === "approved"}
                                onClick={() => handleApproveOrder(order.recommendation_id)}
                              >
                                Approve
                              </button>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => {
                                  setModifyOrderModal(order);
                                  setModifyQty(order.recommended_qty);
                                  setModifySupplier(order.supplier_id);
                                }}
                              >
                                Modify
                              </button>
                              <button
                                className="btn btn-danger btn-sm"
                                disabled={order.decision_status === "rejected"}
                                onClick={() => {
                                  setRejectOrderModal(order);
                                  setRejectReason("");
                                }}
                              >
                                Reject
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "substitutions" && (
            <div className="supply-operation-page">
              <div className="page-header">
                <div className="page-title-group">
                  <h1>Clinical Substitution Manager &amp; Pharmacist Advisor</h1>
                  <p>Pharmacy decides the interchange on an isolated working copy. Purchasing still lives under Recommended Orders.</p>
                </div>
              </div>

              {/* Pharmacist Guidance Banner */}
              <div className="ai-agent-banner" id="pharmacist-advisor">
                <div className="ai-agent-header">
                  <div className="ai-agent-badge">
                    <Sparkles size={14} />
                    Apex Clinical Pharmacy Advisor
                  </div>
                  <span style={{ fontSize: "12px", color: "#94a3b8" }}>Evidence-guided formulary support</span>
                </div>

                <p style={{ fontSize: "13px", color: "#cbd5e1" }}>
                  Review therapeutic equivalence, dosing adjustments, allergy risks, and facility availability before approving a substitution:
                </p>
                <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "6px" }}>
                  Decision support only · Pharmacist review is required before any formulary change.
                </p>

                <div className="ai-agent-chips">
                  <span
                    className="ai-chip"
                    onClick={() => handleAgentQuery("What is the pediatric dosing and surgical prophylaxis equivalence for Cefazolin alternative Cefuroxime?")}
                  >
                    🧪 Pediatric Dosing: Cefazolin vs Cefuroxime
                  </span>
                  <span
                    className="ai-chip"
                    onClick={() => handleAgentQuery("Evaluate Enoxaparin dosing protocol when substituting for Heparin in CrCl < 30 mL/min patients.")}
                  >
                    🩸 Renal Clearance: Enoxaparin vs Heparin
                  </span>
                  <span
                    className="ai-chip"
                    onClick={() => handleAgentQuery("Can Dexmedetomidine substitute for Propofol during mechanical ventilation without inducing delirium?")}
                  >
                    🩺 ICU Sedation: Precedex vs Diprivan
                  </span>
                  <span
                    className="ai-chip"
                    onClick={() => {
                      const target =
                        substitutions.find(
                          (s) => s.shortage_item_id === "SKU-PH-101" && s.alternative_item_id === "SKU-PH-ALT-02"
                        ) || substitutions.find((s) => s.shortage_item_id === "SKU-PH-101");
                      if (target) handleSimulateSubstitution(target);
                    }}
                  >
                    🌿 Simulate impact: switch Cefazolin → Cefuroxime system-wide
                  </span>
                  <span
                    className="ai-chip"
                    onClick={() => {
                      const prompt = "Simulate switching Lisinopril 10mg to Losartan 50mg across all facilities";
                      const target = substitutions.find((s) => s.shortage_item_id === "SKU-PH-112");
                      if (target) handleSimulateSubstitution(target, undefined, undefined, prompt);
                      else handleAgentQuery(prompt);
                    }}
                  >
                    🌿 Simulate switching Lisinopril 10mg → Losartan 50mg
                  </span>
                </div>

                <div className="ai-input-group">
                  <input
                    type="text"
                    placeholder="Ask a clinical question, or 'Simulate switching Lisinopril 10mg to Losartan 50mg across all facilities'"
                    value={agentPrompt}
                    onChange={(e) => setAgentPrompt(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAgentQuery()}
                  />
                  <button
                    className="btn btn-primary"
                    disabled={agentLoading}
                    onClick={() => handleAgentQuery()}
                  >
                    {agentLoading ? <RefreshCw className="spin" size={16} /> : <Send size={16} />}
                    {agentLoading ? "Reviewing..." : "Review Guidance"}
                  </button>
                </div>

                {(agentLoading || agentResponse) && (
                  <div className="ai-response-box">
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                      <strong style={{ color: "#38bdf8", display: "flex", alignItems: "center", gap: "6px" }}>
                        <BrainCircuit size={16} /> Clinical Pharmacy Guidance
                      </strong>
                      <small style={{ color: "#94a3b8" }}>
                        {agentLoading ? "Reviewing the catalog match…" : "Decision support · Pharmacist review required"}
                      </small>
                    </div>
                    <div className="ai-response-content">
                      {agentLoading ? (
                        <p>The advisor is reviewing this substitution in the chat above.</p>
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {agentResponse}
                        </ReactMarkdown>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {(simulating || simulation || simError) && (
                <div className="panel sim-workflow" id="shortage-alt-sim">
                  <div className="panel-header">
                    <div>
                      <h3 className="panel-title">
                        <GitBranch size={18} color="#087c91" />
                        Shortage alternative simulation
                      </h3>
                      <p className="panel-subtitle">
                        The agent investigates on an isolated Lakebase branch, then recommends with evidence. Production stays unchanged until you apply.
                      </p>
                    </div>
                    {simulation?.branch_id && (
                      <span className="badge pending">Working copy {simulation.branch_id}</span>
                    )}
                  </div>
                  <div className="sim-pair">
                    <div>
                      <label>Shortage item</label>
                      <strong>
                        {simulation?.impact?.shortage_item_description || simSource?.shortage_item_description || "Selected shortage"}
                      </strong>
                      <small>
                        {simulation?.impact?.shortage_item_id || simSource?.shortage_item_id}
                      </small>
                    </div>
                    <span className="sim-pair-arrow" aria-hidden="true">→</span>
                    <div>
                      <label>Proposed alternative</label>
                      <strong>
                        {simulation?.impact?.alternative_item_description || simSource?.alternative_item_description || "Selected alternative"}
                      </strong>
                      <small>
                        {simulation?.impact?.alternative_item_id || simSource?.alternative_item_id}
                      </small>
                    </div>
                  </div>
                  <ol className="sim-steps">
                    {["Isolate", "Connect", "Investigate", "Simulate", "Recommend", "Human approves", "Apply to live formulary"].map((label, idx) => {
                      const agentSteps = ["branch", "connect", "investigate", "simulate", "present"];
                      const current = simulation?.steps?.find((step) => step.status === "running");
                      const doneIds = new Set((simulation?.steps || []).filter((step) => step.status === "done").map((step) => step.id));
                      const active =
                        simulating && simulation?.status === "approved"
                          ? idx === 6
                          : simulating && idx < 5
                            ? agentSteps[idx] === (current?.id || agentSteps[Math.min(doneIds.size, 4)])
                          : simulation?.status === "approved"
                            ? idx === 6
                            : simulation?.status === "shipped"
                              ? idx === 6
                              : simulation
                                ? idx === 5
                                : false;
                      const complete =
                        simulation
                          ? (idx < 5 && doneIds.has(agentSteps[idx])) ||
                            ((simulation.status === "approved" || simulation.status === "shipped") && idx === 5) ||
                            (simulation.status === "shipped" && idx === 6)
                          : false;
                      return (
                        <li key={label} className={`${complete ? "done" : ""} ${active ? "active" : ""}`}>
                          <span className="sim-step-index">{idx + 1}</span>
                          {label}
                          {active && simulating && idx < 5 ? <small className="sim-step-live">in progress</small> : null}
                        </li>
                      );
                    })}
                  </ol>
                  {simulation?.status === "running" && (
                    <p className="sim-live-status">
                      {(simulation.steps.find((step) => step.status === "running") || simulation.steps[simulation.steps.length - 1])?.label}
                      {" — "}
                      {(simulation.steps.find((step) => step.status === "running") || simulation.steps[simulation.steps.length - 1])?.detail}
                    </p>
                  )}
                  {simulation?.steps && (
                    <ul className="sim-step-details">
                      {simulation.steps.map((step) => (
                        <li key={step.id} className={step.status === "running" ? "running" : ""}>
                          <strong>{step.label}</strong>
                          <span>{step.detail}</span>
                          <small>{step.status === "running" ? "in progress" : `${step.duration_ms} ms`}</small>
                        </li>
                      ))}
                    </ul>
                  )}
                  {simulating && simulation?.live_transcript && simulation.live_transcript.length > 0 && !simulation.impact && (
                    <details className="sim-transcript" open>
                      <summary>Agent investigation · live on {simulation.branch_id || "working copy"}</summary>
                      <ol>
                        {simulation.live_transcript.map((turn, idx) => (
                          <li key={`${turn.phase}-${idx}`}>
                            <span className="sim-phase">{turn.phase}</span>
                            <p>{turn.thought}</p>
                            <small>
                              <span className="sim-tool">{turn.tool}</span>
                              {" → "}
                              {turn.result}
                            </small>
                          </li>
                        ))}
                      </ol>
                    </details>
                  )}
                  {simError && <p className="sim-error">{simError}</p>}
                  {simulation?.impact && (
                    <>
                      <div className="sim-summary">{simulation.impact.summary}</div>
                      <div className="sim-kpis">
                        <div>
                          <label>Patients / active orders</label>
                          <strong>{simulation.impact.patients_affected.toLocaleString()}</strong>
                        </div>
                        <div>
                          <label>Monthly cost impact</label>
                          <strong>
                            {simulation.impact.monthly_cost_delta < 0 ? "−" : "+"}$
                            {Math.abs(simulation.impact.monthly_cost_delta).toLocaleString()}
                          </strong>
                          {simulation.impact.naive_monthly_cost_delta != null && (
                            <small style={{ display: "block", color: "#64748b" }}>
                              Naive 1:1 calc +${simulation.impact.naive_monthly_cost_delta.toLocaleString()}
                            </small>
                          )}
                        </div>
                        <div>
                          <label>Allergy / contraindication flags</label>
                          <strong>
                            {simulation.impact.allergy_flags} / {simulation.impact.contraindications}
                          </strong>
                        </div>
                        <div>
                          <label>90-day cover</label>
                          <strong>{simulation.impact.covers_90d ? "Covered" : "Short"}</strong>
                        </div>
                      </div>
                      {simulation.impact.agent?.categories && simulation.impact.agent.categories.length > 0 && (
                        <div className="sim-categories">
                          {simulation.impact.agent.categories.map((cat) => (
                            <div key={cat.key} className={`sim-cat sim-cat-${cat.severity}`}>
                              <strong>
                                {cat.key}. {cat.label}
                              </strong>
                              <em>{cat.patients.toLocaleString()} patients ({Math.round(cat.share * 1000) / 10}%)</em>
                              <p>{cat.recommendation}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      {simulation.impact.agent?.unexpected && simulation.impact.agent.unexpected.length > 0 && (
                        <div className="sim-unexpected">
                          <strong>Unexpected findings</strong>
                          <ul>
                            {simulation.impact.agent.unexpected.map((note) => (
                              <li key={note}>{note}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {((simulation.impact.agent?.transcript && simulation.impact.agent.transcript.length > 0)
                        || (simulation.live_transcript && simulation.live_transcript.length > 0)) && (
                        <details className="sim-transcript" open>
                          <summary>
                            Agent investigation ({simulation.impact.agent?.planner || "branch SQL"})
                            {simulating ? " · live" : ""}
                          </summary>
                          <ol>
                            {(simulation.impact.agent?.transcript || simulation.live_transcript || []).map((turn, idx) => (
                              <li key={`${turn.phase}-${idx}`}>
                                <span className="sim-phase">{turn.phase}</span>
                                <p>{turn.thought}</p>
                                <small>
                                  <span className="sim-tool">{turn.tool}</span>
                                  {" → "}
                                  {turn.result}
                                </small>
                              </li>
                            ))}
                          </ol>
                        </details>
                      )}
                      {simulation.impact.agent?.report_markdown && (
                        <div className="sim-report">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {simulation.impact.agent.report_markdown}
                          </ReactMarkdown>
                        </div>
                      )}
                      <div className="table-container">
                        <table>
                          <thead>
                            <tr>
                              <th>Include</th>
                              <th>Facility</th>
                              <th>Patients</th>
                              <th>Allocated units</th>
                              <th>Days cover</th>
                              <th>Lead time</th>
                              <th>Monthly $</th>
                            </tr>
                          </thead>
                          <tbody>
                            {simulation.impact.facilities.map((fac) => (
                              <tr key={fac.facility_id}>
                                <td>
                                  <input
                                    type="checkbox"
                                    checked={simFacilityIds.includes(fac.facility_id)}
                                    onChange={(e) =>
                                      setSimFacilityIds((prev) =>
                                        e.target.checked
                                          ? [...prev, fac.facility_id]
                                          : prev.filter((id) => id !== fac.facility_id)
                                      )
                                    }
                                  />
                                </td>
                                <td>
                                  {fac.facility_name}
                                  <small style={{ display: "block", color: "#64748b" }}>{fac.facility_id}</small>
                                </td>
                                <td>{fac.patients}</td>
                                <td>{fac.units_allocated}</td>
                                <td>{fac.days_cover === 999 ? "—" : wholeNumber(fac.days_cover)}</td>
                                <td>
                                  {fac.lead_time_delta_days > 0 ? (
                                    <span className="badge pending">+{wholeNumber(fac.lead_time_delta_days)}d</span>
                                  ) : (
                                    <span className="badge ready">unchanged</span>
                                  )}
                                </td>
                                <td>
                                  {fac.monthly_cost_delta < 0 ? "−" : "+"}$
                                  {Math.abs(fac.monthly_cost_delta).toLocaleString()}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {simulation.status === "presented" && (
                        <div className="sim-actions">
                          <button className="btn btn-primary" disabled={simulating} onClick={() => handleSimDecision("approved")}>
                            Approve plan
                          </button>
                          <button className="btn btn-secondary" disabled={simulating || simFacilityIds.length === 0} onClick={() => handleSimDecision("modified")}>
                            Re-simulate selected facilities
                          </button>
                          <button className="btn btn-danger" disabled={simulating} onClick={() => handleSimDecision("rejected")}>
                            Discard simulation
                          </button>
                        </div>
                      )}
                      {simulation.status === "approved" && (
                        <div className="sim-replay">
                          <div>
                            <strong>Human approval recorded</strong>
                            <p>
                              Production is still unchanged. Apply this approved substitution to the live formulary, then close the working simulation.
                            </p>
                          </div>
                          <button className="btn btn-primary" disabled={simulating} onClick={handleReplayToProduction}>
                            {simulating ? "Applying…" : "Apply to live formulary"}
                          </button>
                          <button className="btn btn-danger" disabled={simulating} onClick={() => handleSimDecision("rejected")}>
                            Discard approved plan
                          </button>
                        </div>
                      )}
                      {simulation.status === "shipped" && (
                        <p className="panel-subtitle" style={{ padding: "8px 16px 16px" }}>
                          The approved substitution is now live on the formulary. The working simulation has been closed.
                        </p>
                      )}
                    </>
                  )}
                </div>
              )}

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">
                    <BrainCircuit size={18} color="#087c91" />
                    Shortage substitutions
                  </h3>
                  <span className="badge pending">{shortageGroups.length} shortages</span>
                </div>
                <p className="panel-subtitle" style={{ padding: "0 16px 8px" }}>
                  Approve a formulary alternative for the shortage, or review additional catalog matches for the same item before authorizing.
                </p>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Shortage Item</th>
                        <th>Recommended Alternative</th>
                        <th>Equivalence</th>
                        <th>Formulary Status</th>
                        <th>Stock Status</th>
                        <th>Clinical Rationale</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {shortageGroups.map(([shortageId, rows]) => {
                        const shortage = rows[0];
                        const expanded = expandedShortageId === shortageId;
                        const catalog = similarByItem[shortageId];
                        const listed = new Set(rows.map((row) => row.alternative_item_id).concat(shortageId));
                        const extraMatches = (catalog?.matches || []).filter((match) => !listed.has(match.item_id));
                        return (
                          <React.Fragment key={shortageId}>
                            {rows.map((sub, idx) => (
                              <tr key={sub.substitution_id}>
                                <td>
                                  {idx === 0 ? (
                                    <>
                                      <strong>{sub.shortage_item_description}</strong>
                                      <small style={{ color: "#64748b", display: "block" }}>{sub.shortage_item_id}</small>
                                    </>
                                  ) : (
                                    <small style={{ color: "#94a3b8" }}>same shortage</small>
                                  )}
                                </td>
                                <td>
                                  <strong>{sub.alternative_item_description}</strong>
                                  <small style={{ color: "#087c91", display: "block" }}>{sub.alternative_item_id}</small>
                                </td>
                                <td>
                                  <span className={`badge ${sub.clinical_equivalence === "equivalent" ? "ready" : "pending"}`}>
                                    {sub.clinical_equivalence}
                                  </span>
                                </td>
                                <td>
                                  <span className={`badge ${sub.formulary_status === "on_formulary" ? "ready" : "emergency"}`}>
                                    {sub.formulary_status.replaceAll("_", " ")}
                                  </span>
                                </td>
                                <td>
                                  <span className={`badge ${sub.availability === "in_stock" ? "ready" : "pending"}`}>
                                    {sub.availability.replaceAll("_", " ")}
                                  </span>
                                </td>
                                <td style={{ maxWidth: "340px", fontSize: "12px", color: "#334155" }}>
                                  {sub.agent_reasoning}
                                </td>
                                <td>
                                  <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                                    {idx === 0 && (
                                      <button
                                        className="btn btn-secondary btn-sm"
                                        onClick={() => {
                                          if (expanded) {
                                            setExpandedShortageId(null);
                                            return;
                                          }
                                          openShortageAlternatives(sub.shortage_item_id, sub.shortage_item_description);
                                        }}
                                      >
                                        {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                                        {expanded ? "Hide catalog matches" : "More catalog matches"}
                                      </button>
                                    )}
                                    <button
                                      className="btn btn-secondary btn-sm"
                                      disabled={simulating}
                                      onClick={() => handleSimulateSubstitution(sub)}
                                    >
                                      <GitBranch size={12} /> Simulate impact
                                    </button>
                                    <button
                                      className="btn btn-primary btn-sm"
                                      onClick={() => {
                                        setSelectSubModal(sub);
                                        setClinicalNotes("");
                                      }}
                                    >
                                      Approve Alternative
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                            {expanded && catalog?.loading && (
                              <tr className="catalog-match-row">
                                <td colSpan={7}>Loading additional catalog matches for this shortage…</td>
                              </tr>
                            )}
                            {expanded && !catalog?.loading && extraMatches.length === 0 && (
                              <tr className="catalog-match-row">
                                <td colSpan={7}>No additional catalog matches beyond the formulary alternatives already listed.</td>
                              </tr>
                            )}
                            {expanded && extraMatches.map((match) => (
                              <tr className="catalog-match-row" key={`${shortageId}-${match.item_id}`}>
                                <td>
                                  <small className="shortage-group-label">Additional catalog match</small>
                                </td>
                                <td>
                                  <strong>{match.item_description}</strong>
                                  <small style={{ color: "#087c91", display: "block" }}>{match.item_id}</small>
                                </td>
                                <td>
                                  <span className="badge pending">{Math.round(Number(match.similarity || 0) * 100)}% similar</span>
                                </td>
                                <td>—</td>
                                <td>—</td>
                                <td style={{ maxWidth: "340px", fontSize: "12px", color: "#334155" }}>
                                  Adjacent catalog item for this shortage. Review with the advisor before authorizing.
                                </td>
                                <td>
                                  <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                                    <button
                                      className="btn btn-secondary btn-sm"
                                      onClick={() =>
                                        handleAgentQuery(
                                          `Evaluate substituting ${shortage.shortage_item_description} (${shortage.shortage_item_id}) with ${match.item_description} (${match.item_id}).`
                                        )
                                      }
                                    >
                                      Ask advisor
                                    </button>
                                    <button
                                      className="btn btn-primary btn-sm"
                                      onClick={() => {
                                        setSelectSubModal({
                                          ...shortage,
                                          alternative_item_id: match.item_id,
                                          alternative_item_description: match.item_description,
                                          clinical_equivalence: "review",
                                          formulary_status: "catalog_match",
                                          availability: "review",
                                          agent_reasoning: `Catalog match ${Math.round(Number(match.similarity || 0) * 100)}% similar to shortage item`,
                                        });
                                        setClinicalNotes(`Catalog match for ${shortage.shortage_item_id}: ${match.item_id}.`);
                                      }}
                                    >
                                      Approve Alternative
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </React.Fragment>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "recalls" && (
            <div className="supply-operation-page">
              <div className="page-header">
                <div className="page-title-group">
                  <h1>FDA Recall Exposure & Quarantine Protocol</h1>
                  <p>Trace affected lots across facilities, protect exposed patients, and execute auditable quarantines.</p>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">
                    <ShieldAlert size={18} color="#dc2626" />
                    Active Recalls by Facility & Lot
                  </h3>
                  <span className="badge critical">3 Active FDA Notices</span>
                </div>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Recall Number & Class</th>
                        <th>Item & Affected Lot</th>
                        <th>Facility & Physical Location</th>
                        <th>On-Hand Lot Qty</th>
                        <th>Patient Exposure Count</th>
                        <th>Status</th>
                        <th>Action Workflow</th>
                      </tr>
                    </thead>
                    <tbody>
                      {uniqueRecalls.map((recall) => (
                        <React.Fragment key={recall.recall_id}>
                        <tr>
                          <td>
                            <strong>{recall.fda_recall_number}</strong>
                            <span
                              className={`badge ${recall.recall_class === "I" ? "critical" : recall.recall_class === "II" ? "high" : "medium"}`}
                              style={{ display: "inline-block", marginTop: "4px" }}
                            >
                              Class {recall.recall_class} Recall
                            </span>
                          </td>
                          <td>
                            <strong style={{ display: "block" }}>{recall.item_description}</strong>
                            <code
                              style={{
                                display: "block",
                                marginTop: "6px",
                                width: "fit-content",
                                fontSize: "11px",
                                backgroundColor: "#fee2e2",
                                padding: "2px 6px",
                                borderRadius: "4px",
                                overflowWrap: "anywhere",
                                wordBreak: "break-word",
                              }}
                            >
                              {recall.affected_lot}
                            </code>
                          </td>
                          <td>
                            <strong>{recall.facility_name}</strong>
                            <small style={{ color: "#64748b", display: "block" }}>{recall.location_in_facility}</small>
                          </td>
                          <td><strong>{recall.qty_on_hand}</strong> units</td>
                          <td>
                            <strong style={{ color: recall.patient_exposure_count > 0 ? "#dc2626" : "#10b981" }}>
                              {recall.patient_exposure_count} patients
                            </strong>
                          </td>
                          <td>
                            <span className={`badge ${recall.status === "open" ? "critical" : "ready"}`}>
                              {recall.status}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: "6px" }}>
                              <button
                                className="btn btn-danger btn-sm"
                                disabled={recall.status === "quarantined"}
                                onClick={() => handleRecallAction(recall.recall_id, "quarantined")}
                              >
                                Quarantine Lot
                              </button>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleRecallAction(recall.recall_id, "traced_patients")}
                              >
                                {tracedRecallId === recall.recall_id ? "Hide Patients" : "Trace Patients"}
                              </button>
                            </div>
                          </td>
                        </tr>
                        {tracedRecallId === recall.recall_id && (
                          <tr key={`${recall.recall_id}-patients`} className="patient-trace-row">
                            <td colSpan={7}>
                              <div className="patient-trace-panel">
                                <strong>Traced patient exposure · {recall.facility_name}</strong>
                                <p>This roster stays hidden until Trace Patients is selected. Contact tracing is recorded to the audit log without closing the recall.</p>
                                <div className="table-container">
                                  <table>
                                    <thead>
                                      <tr>
                                        <th>MRN</th>
                                        <th>Encounter</th>
                                        <th>Unit / Location</th>
                                        <th>Lot</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {exposurePatients(recall).slice(0, 12).map((patient) => (
                                        <tr key={patient.mrn}>
                                          <td><code>{patient.mrn}</code></td>
                                          <td>{patient.encounter}</td>
                                          <td>{patient.unit}</td>
                                          <td>
                                            <code style={{ overflowWrap: "anywhere", wordBreak: "break-word" }}>
                                              {recall.affected_lot}
                                            </code>
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "transfers" && (
            <div className="supply-operation-page">
              <div className="page-header">
                <div className="page-title-group">
                  <h1>Inter-Facility Inventory Rebalancing</h1>
                  <p>Network planning recommendations rebalance inventory across Apex facilities to relieve local shortages without new purchase orders.</p>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">
                    <ArrowRightLeft size={18} color="#087c91" />
                    Recommended Inventory Transfer Runs ({uniqueTransfers.length} Routes)
                  </h3>
                </div>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>From Source Facility</th>
                        <th>To Destination Facility</th>
                        <th>Transfer Qty</th>
                        <th>Reason</th>
                        <th>Impact on Supply</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {uniqueTransfers.map((t) => (
                        <tr key={t.transfer_id}>
                          <td>
                            <strong>{t.item_description}</strong>
                            <small style={{ color: "#64748b", display: "block" }}>{t.item_id}</small>
                          </td>
                          <td>
                            <strong>{t.from_facility_name}</strong>
                            <small style={{ color: "#10b981", display: "block" }}>{wholeNumber(t.from_days_of_supply)}d on-hand</small>
                          </td>
                          <td>
                            <strong>{t.to_facility_name}</strong>
                            <small style={{ color: "#dc2626", display: "block" }}>Critically low ({wholeNumber(t.to_days_of_supply)}d)</small>
                          </td>
                          <td><strong>{t.recommended_qty}</strong> units</td>
                          <td>
                            <span className="badge pending">{t.reason.replace("_", " ")}</span>
                          </td>
                          <td>
                            <span style={{ fontSize: "11px", color: "#047857" }}>
                              Boosts destination to {wholeNumber(Number(t.to_days_of_supply) + 8.5)} days
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${t.status === "approved" ? "ready" : "pending"}`}>
                              {t.status}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: "6px" }}>
                              <button
                                className="btn btn-primary btn-sm"
                                disabled={t.status === "approved"}
                                onClick={() => handleTransferConfirm(t.transfer_id, "approved")}
                              >
                                Approve Route
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "decision-insights" && (
            <div className="supply-operation-page">
              <div className="page-header">
                <div className="page-title-group">
                  <h1>Operational Decision Insights</h1>
                  <p>
                    Human decisions written in Lakebase stream into the lakehouse change-data feed, then this view.
                    Use it to show how operational actions become enterprise history.
                  </p>
                </div>
                <div className="page-actions">
                  <span className="live-metrics-chip">
                    <BarChart3 size={14} /> {decisionInsights?.source_label || "Decision history"}
                  </span>
                </div>
              </div>

              <div className="kpi-grid">
                {(decisionInsights?.kpis || []).map((kpi: KPI, idx: number) => (
                  <div key={kpi.label} className="kpi-card">
                    <div className="kpi-header">
                      <span className="kpi-label">{kpi.label}</span>
                      <div className={`kpi-icon ${kpi.status}`}>
                        {idx === 0 && <BarChart3 size={18} />}
                        {idx === 1 && <FileText size={18} />}
                        {idx === 2 && <BrainCircuit size={18} />}
                        {idx === 3 && <ShieldAlert size={18} />}
                      </div>
                    </div>
                    <div className="kpi-value">{kpi.value}</div>
                    <div className="kpi-subtext">{kpi.subtext}</div>
                    <div className={`kpi-trend ${kpi.status}`}>{kpi.trend}</div>
                  </div>
                ))}
              </div>

              <div className="insight-grid">
                <div className="panel">
                  <div className="panel-header">
                    <h3 className="panel-title">Decisions by family</h3>
                  </div>
                  <InsightBars rows={decisionInsights?.by_family || []} />
                </div>
                <div className="panel">
                  <div className="panel-header">
                    <h3 className="panel-title">Order outcomes</h3>
                  </div>
                  <InsightBars rows={decisionInsights?.order_outcomes || []} />
                </div>
                <div className="panel">
                  <div className="panel-header">
                    <h3 className="panel-title">Recall actions</h3>
                  </div>
                  <InsightBars rows={decisionInsights?.recall_actions || []} />
                </div>
                <div className="panel">
                  <div className="panel-header">
                    <h3 className="panel-title">Decisions by operator</h3>
                  </div>
                  <InsightBars rows={decisionInsights?.by_actor || []} />
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">Authorized substitutions</h3>
                  <span className="badge pending">From CDF history</span>
                </div>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Shortage item</th>
                        <th>Selected alternative</th>
                        <th>Times selected</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(decisionInsights?.substitution_pairs || []).length === 0 && (
                        <tr><td colSpan={3}>No substitution selections have streamed yet.</td></tr>
                      )}
                      {(decisionInsights?.substitution_pairs || []).map((row: any) => (
                        <tr key={`${row.shortage_item_id}-${row.selected_alternative_id}`}>
                          <td>
                            <strong>{row.shortage_item}</strong>
                            <small style={{ display: "block", color: "#64748b" }}>{row.shortage_item_id}</small>
                          </td>
                          <td>
                            <strong>{row.selected_alternative}</strong>
                            <small style={{ display: "block", color: "#087c91" }}>{row.selected_alternative_id}</small>
                          </td>
                          <td>{row.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">Activity by day</h3>
                </div>
                <div className="insight-timeline">
                  {(decisionInsights?.timeline || []).length === 0 && <p className="insight-empty">No dated events yet.</p>}
                  {(decisionInsights?.timeline || []).map((day: any) => {
                    const total = (day.orders || 0) + (day.substitutions || 0) + (day.recalls || 0);
                    return (
                      <div key={day.day} className="insight-day">
                        <strong>{day.day}</strong>
                        <div className="insight-day-stack">
                          <span className="orders" style={{ width: `${total ? (day.orders / total) * 100 : 0}%` }} title={`${day.orders} orders`} />
                          <span className="subs" style={{ width: `${total ? (day.substitutions / total) * 100 : 0}%` }} title={`${day.substitutions} substitutions`} />
                          <span className="recalls" style={{ width: `${total ? (day.recalls / total) * 100 : 0}%` }} title={`${day.recalls} recalls`} />
                        </div>
                        <small>{day.orders} orders · {day.substitutions} substitutions · {day.recalls} recalls</small>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">Recent decision feed</h3>
                </div>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>When</th>
                        <th>Family</th>
                        <th>Action</th>
                        <th>Operator</th>
                        <th>Detail</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(decisionInsights?.recent || []).map((row: any, idx: number) => (
                        <tr key={`${row.occurred_at}-${idx}`}>
                          <td>{String(row.occurred_at || "").replace("T", " ").slice(0, 19)}</td>
                          <td>{row.family}</td>
                          <td><span className="badge pending">{String(row.action || "").replaceAll("_", " ")}</span></td>
                          <td>{row.actor}</td>
                          <td style={{ maxWidth: "360px", fontSize: "12px" }}>{row.detail}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === "platform-admin" && (
            <div>
              <div className="page-header">
                <div className="page-title-group">
                  <h1>Platform Administration</h1>
                  <p>Architecture, data-service health, feature branches, credentials, access controls, and schema governance.</p>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">
                    <Workflow size={18} color="#087c91" />
                    Closed-Loop Intelligence Architecture
                  </h3>
                  <span className={`badge ${flowStatus?.live ? "ready" : "high"}`}>
                    {flowStatus?.live ? "Live loop" : "Waiting for telemetry"}
                  </span>
                </div>
                <ArchitectureFlow
                  flow={flowStatus}
                  selected={selectedStage}
                  onSelect={setSelectedStage}
                  onSimulate={handleSimulateInventory}
                  simulating={simulating}
                />
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">Data Product Flow Status</h3>
                  <span className="badge ready">
                    {selectedStage === "feedback" ? "Decision events" : "Published products"}
                  </span>
                </div>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>{selectedStage === "feedback" ? "Operational Source" : "Analytical Source"}</th>
                        <th>{selectedStage === "feedback" ? "Analytics Target" : "Operational Data Product"}</th>
                        <th>Refresh Mode</th>
                        <th>Last Change</th>
                        <th>Lakebase Records</th>
                        <th>Gold Records</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(selectedStage === "feedback"
                        ? flowStatus?.lakebase_to_delta_cdf || []
                        : flowStatus?.synced_tables || []
                      ).map((row: any) => {
                        const source = row.lakehouse_source || row.lakebase_table;
                        const target = row.lakebase_target || row.delta_target;
                        const status = row.status || "Unknown";
                        const badge =
                          status === "Healthy" || status === "Streaming" || status === "Snapshotting"
                            ? "ready"
                            : status === "Drift"
                              ? "high"
                              : "critical";
                        return (
                          <tr key={`${source}-${target}`}>
                            <td><code>{source}</code></td>
                            <td><code>{target}</code></td>
                            <td>{row.sync_mode || row.cdc_mechanism}</td>
                            <td><strong>{row.latency || row.event_lag || "—"}</strong></td>
                            <td>{Number(row.records_synced ?? 0).toLocaleString()}</td>
                            <td>{row.gold_records == null ? "—" : Number(row.gold_records).toLocaleString()}</td>
                            <td><span className={`badge ${badge}`}>{status}</span></td>
                          </tr>
                        );
                      })}
                      {((selectedStage === "feedback"
                        ? flowStatus?.lakebase_to_delta_cdf
                        : flowStatus?.synced_tables) || []).length === 0 && (
                        <tr>
                          <td colSpan={7}>
                            {flowStatus == null
                              ? "Loading live data product counts…"
                              : "No data products returned for this hop."}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Runtime Health Panel */}
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h3 className="panel-title">
                      <Activity size={18} color="#087c91" />
                      Data Service Runtime
                    </h3>
                    <p className="panel-subtitle">Implementation health and serving performance for platform administrators</p>
                  </div>
                  <span className={`badge ${health.connected ? "ready" : "critical"}`}>
                    {health.connected ? "Connected" : "Unavailable"}
                  </span>
                </div>
                <div className="kpi-grid">
                  <div className="kpi-card">
                    <div className="kpi-label">Compute Capacity</div>
                    <div className="kpi-value">
                      {compute.observed_at == null ? "…" : `${wholeNumber(compute.current_cu)} CU`}
                    </div>
                    <div className="kpi-subtext">
                      Auto-Scaling range: {wholeNumber(compute.min_cu, 1)}–{wholeNumber(compute.max_cu, 1)} CU
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Active Queries</div>
                    <div className="kpi-value">{Number(compute.active_queries ?? 0)}</div>
                    <div className="kpi-subtext">
                      {Number(compute.connections ?? 0)} open connections · {Number(compute.idle_connections ?? 0)} idle
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Database Throughput</div>
                    <div className="kpi-value" style={{ fontSize: "24px" }}>
                      {Number(compute.transactions_per_second ?? 0).toFixed(2)} TPS
                    </div>
                    <div className="kpi-subtext">
                      {Number(compute.connection_utilization_pct ?? 0).toFixed(1)}% connection utilization ·{" "}
                      {Number(compute.transactions_rolled_back ?? 0).toLocaleString()} rollbacks
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Runtime Status</div>
                    <div className="kpi-value" style={{ fontSize: "24px", textTransform: "capitalize" }}>
                      {compute.observed_at == null
                        ? "Loading…"
                        : String(compute.state || health.status || "Unknown").replace(/_/g, " ").toLowerCase()}
                    </div>
                    <div className="kpi-subtext">
                      {health.latency_ms ?? "—"} ms health probe · {compute.idle_connections ?? 0} idle
                      {compute.last_active_time ? ` · last active ${new Date(compute.last_active_time).toLocaleTimeString()}` : ""}
                    </div>
                  </div>
                </div>
              </div>

              {/* Branch Manager Panel */}
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h3 className="panel-title">
                      <GitBranch size={18} color="#087c91" />
                      Database Environment
                    </h3>
                    <p className="panel-subtitle">
                      {branches.length} environment{branches.length === 1 ? "" : "s"} · copy-on-write production, development, and feature branches
                    </p>
                  </div>
                  <div className="page-actions">
                    <button className="btn btn-secondary btn-sm" onClick={() => fetchData(true)}>
                      <RefreshCw size={14} /> Refresh
                    </button>
                  </div>
                </div>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Environment ID</th>
                        <th>Create branch</th>
                        <th>Type</th>
                        <th>Endpoint Host</th>
                        <th>Credentials &amp; Roles</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {branches.map((b) => {
                        const parentName = b.parent || (b.default ? null : "production");
                        const typeLabel = branchTypeLabel(b);
                        const hoverLabel = parentName
                          ? `${typeLabel} of ${parentName}`
                          : "Primary environment";
                        return (
                        <tr key={b.id} title={hoverLabel}>
                          <td title={hoverLabel}>
                            <strong>{b.id}</strong>
                            {b.default && (
                              <span className="badge ready" style={{ marginLeft: "8px" }}>Primary</span>
                            )}
                          </td>
                          <td>
                            <button
                              className="btn btn-primary btn-sm"
                              onClick={() => {
                                setBranchParent(b.id);
                                setCreateBranchModal(true);
                              }}
                            >
                              <Plus size={12} /> Create branch
                            </button>
                          </td>
                          <td>
                            <span className={`badge ${typeLabel === "Agent Branch" ? "pending" : b.default ? "ready" : "pending"}`}>
                              {typeLabel}
                            </span>
                          </td>
                          <td>
                            <code style={{ fontSize: "11px", backgroundColor: "#f1f5f9", padding: "3px 6px", borderRadius: "4px" }}>
                              {b.connection?.host || "ep-mock.database.cloud.databricks.com"}
                            </code>
                          </td>
                          <td>
                            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                              <div style={{ display: "flex", gap: "6px" }}>
                                <button
                                  className="btn btn-secondary btn-sm"
                                  onClick={() => handleGenerateCred(b.id)}
                                >
                                  <Key size={12} /> Mint Token
                                </button>
                                <button
                                  className="btn btn-secondary btn-sm"
                                  onClick={() => setRoleModal(b.id)}
                                >
                                  <UserCheck size={12} /> Assign Role
                                </button>
                              </div>
                              {(b.roles || []).length > 0 ? (
                                <small style={{ color: "#64748b" }}>
                                  {(b.roles || []).map((role) => (
                                    <span key={`${role.id}-${role.purpose}`} style={{ display: "block" }}>
                                      {role.purpose === "agent" ? "Agent" : role.purpose === "app" ? "App" : "Role"}: {role.identity}
                                    </span>
                                  ))}
                                </small>
                              ) : (
                                <small style={{ color: "#94a3b8" }}>
                                  {b.id === "production" ? "App identity only (not the substitution agent)" : "No agent role"}
                                </small>
                              )}
                            </div>
                          </td>
                          <td>
                            <div className="env-row-actions">
                            {b.id !== "production" ? (
                              <button
                                className="btn btn-danger btn-sm"
                                onClick={() => handleDeleteBranch(b.id)}
                              >
                                <Trash2 size={12} /> Delete
                              </button>
                            ) : (
                              <span style={{ fontSize: "11px", color: "#94a3b8" }}>Protected</span>
                            )}
                            <div className="branch-hover">
                              <button type="button" className="branch-hover-trigger" aria-label={`Hierarchy for ${b.id}`}>
                                <Network size={16} />
                              </button>
                              <div className="branch-hover-card">
                                <small>Branch hierarchy</small>
                                <BranchTree branches={branches} highlightId={b.id} />
                              </div>
                            </div>
                            </div>
                          </td>
                        </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Applied Migrations Panel */}
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h3 className="panel-title">
                      <Layers size={18} color="#087c91" />
                      Schema Migrations History (SHA-256 Verified)
                    </h3>
                    <p className="panel-subtitle">Tracks exactly-once schema evolution across production and feature branches</p>
                  </div>
                </div>

                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Migration Script</th>
                        <th>SHA-256 Checksum</th>
                        <th>Applied At</th>
                        <th>Applied By</th>
                        <th>Verification Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {migrations.map((m, idx) => (
                        <tr key={idx}>
                          <td><strong>{m.version}</strong></td>
                          <td>
                            <code style={{ fontSize: "11px", backgroundColor: "#f1f5f9", padding: "2px 6px", borderRadius: "4px" }}>
                              {m.checksum?.substring(0, 16)}...
                            </code>
                          </td>
                          <td>{m.applied_at || "Just now"}</td>
                          <td>{m.applied_by || "admin@apexhealth.org"}</td>
                          <td>
                            <span className="badge ready">Applied &amp; Verified</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* ==================================================== */}
      {/* MODALS */}
      {/* ==================================================== */}

      {/* Item Detail Modal */}
      {selectedRiskItem && (
        <div className="modal-overlay" onClick={() => setSelectedRiskItem(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedRiskItem.item_description}</h3>
              <button onClick={() => setSelectedRiskItem(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                <span className={`badge ${selectedRiskItem.risk_tier}`}>
                  Risk Score: {selectedRiskItem.risk_score} / 100
                </span>
                <span className="badge pending">{selectedRiskItem.item_category}</span>
                <span style={{ fontSize: "12px", color: "#64748b" }}>SKU: {selectedRiskItem.item_id}</span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginTop: "12px" }}>
                <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px" }}>
                  <small style={{ color: "#64748b" }}>Current On-Hand</small>
                  <p style={{ fontSize: "20px", fontWeight: 700 }}>{selectedRiskItem.current_on_hand} units</p>
                </div>
                <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px" }}>
                  <small style={{ color: "#64748b" }}>Days of Supply</small>
                  <p style={{ fontSize: "20px", fontWeight: 700, color: selectedRiskItem.days_of_supply < 3 ? "#dc2626" : "#0f172a" }}>
                    {wholeNumber(selectedRiskItem.days_of_supply)} days
                  </p>
                </div>
                <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px" }}>
                  <small style={{ color: "#64748b" }}>30-Day Demand Forecast</small>
                  <p style={{ fontSize: "20px", fontWeight: 700 }}>{selectedRiskItem.forecast_demand_30d} units</p>
                </div>
                <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px" }}>
                  <small style={{ color: "#64748b" }}>90-Day Demand Forecast</small>
                  <p style={{ fontSize: "20px", fontWeight: 700 }}>{selectedRiskItem.forecast_demand_90d} units</p>
                </div>
              </div>

              <div style={{ marginTop: "14px" }}>
                <strong>Predictive Risk Factors</strong>
                <RiskFactorList factors={selectedRiskItem.risk_factors} />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-primary"
                onClick={() => {
                  setSelectedRiskItem(null);
                  setPersona("pharmacist");
                  setActiveTab("substitutions");
                  openShortageAlternatives(selectedRiskItem.item_id, selectedRiskItem.item_description);
                  handleAgentQuery(`Evaluate clinical alternatives for shortage item ${selectedRiskItem.item_description}`);
                }}
              >
                <BrainCircuit size={16} /> Review Clinical Alternatives
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modify Order Modal */}
      {modifyOrderModal && (
        <div className="modal-overlay" onClick={() => setModifyOrderModal(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Modify Recommended PO #{modifyOrderModal.recommendation_id}</h3>
              <button onClick={() => setModifyOrderModal(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: "13px", color: "#64748b" }}>
                {modifyOrderModal.item_description} for {modifyOrderModal.facility_name}
              </p>
              <div className="form-group">
                <label>Adjust Order Quantity</label>
                <input
                  type="number"
                  className="form-control"
                  value={modifyQty}
                  onChange={(e) => setModifyQty(parseInt(e.target.value) || 0)}
                />
              </div>
              <div className="form-group">
                <label>Supplier</label>
                <input
                  type="text"
                  className="form-control"
                  value={modifySupplier}
                  onChange={(e) => setModifySupplier(e.target.value)}
                />
              </div>
              <p style={{ fontSize: "12px", color: "#087c91" }}>
                Projected New Cost: ${(modifyQty * modifyOrderModal.unit_cost).toLocaleString()}
              </p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModifyOrderModal(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleModifyOrder}>
                Save Modification
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Order Modal */}
      {rejectOrderModal && (
        <div className="modal-overlay" onClick={() => setRejectOrderModal(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Reject Recommended PO #{rejectOrderModal.recommendation_id}</h3>
              <button onClick={() => setRejectOrderModal(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Rejection Reason for Audit Trail</label>
                <textarea
                  className="form-control"
                  placeholder="Specify clinical or budgetary reason for rejection..."
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setRejectOrderModal(null)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleRejectOrder}>
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Select Substitution Modal */}
      {selectSubModal && (
        <div className="modal-overlay" onClick={() => setSelectSubModal(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Approve Clinical Alternative</h3>
              <button onClick={() => setSelectSubModal(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: "13px" }}>
                Substituting <strong>{selectSubModal.shortage_item_description}</strong> with{" "}
                <strong style={{ color: "#087c91" }}>{selectSubModal.alternative_item_description}</strong>.
              </p>
              <div className="form-group">
                <label>Clinical &amp; Dosage Conversion Notes</label>
                <textarea
                  className="form-control"
                  placeholder="Document pharmacist clinical justification, renal dosing check, and infusion instructions..."
                  value={clinicalNotes}
                  onChange={(e) => setClinicalNotes(e.target.value)}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setSelectSubModal(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSelectSub}>
                Authorize Clinical Substitution
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Feature Branch Modal */}
      {createBranchModal && (
        <div className="modal-overlay" onClick={() => setCreateBranchModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create feature branch</h3>
              <button onClick={() => setCreateBranchModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: "13px", color: "#64748b" }}>
                Spins up an isolated, zero-copy clone of <strong>{branchParent || "production"}</strong> in &lt; 1 second for schema testing and PR validation.
              </p>
              <div className="form-group">
                <label>Feature branch identifier</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. pr-42-expiration-alerts or feat-pediatric-sku"
                  value={newBranchId}
                  onChange={(e) => setNewBranchId(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Auto-Expiration TTL (Time-To-Live)</label>
                <select
                  className="form-control"
                  value={newBranchTTL}
                  onChange={(e) => setNewBranchTTL(parseInt(e.target.value))}
                >
                  <option value={86400}>24 Hours (Standard PR)</option>
                  <option value={172800}>48 Hours</option>
                  <option value={604800}>7 Days</option>
                  <option value={0}>No Expiration (Persistent)</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setCreateBranchModal(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleCreateBranch}>
                Create feature branch
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Credential Generated Modal */}
      {credentialModal && (
        <div className="modal-overlay" onClick={() => setCredentialModal(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Generated Database Credential</h3>
              <button onClick={() => setCredentialModal(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p style={{ fontSize: "13px", color: "#166534", backgroundColor: "#f0fdf4", padding: "10px", borderRadius: "8px" }}>
                Short-lived OAuth token generated successfully! Valid for 1 hour.
              </p>
              <div className="form-group">
                <label>Endpoint Host</label>
                <input type="text" readOnly className="form-control" value={credentialModal.host} />
              </div>
              <div className="form-group">
                <label>User</label>
                <input type="text" readOnly className="form-control" value={credentialModal.user} />
              </div>
              <div className="form-group">
                <label>Token (Password)</label>
                <input
                  type="text"
                  readOnly
                  className="form-control"
                  value={credentialModal.token}
                  style={{ fontFamily: "monospace", fontSize: "11px" }}
                />
              </div>
              <div className="form-group">
                <label>Direct psql Connection String</label>
                <div style={{ display: "flex", gap: "8px" }}>
                  <input
                    type="text"
                    readOnly
                    className="form-control"
                    value={`psql "sslmode=require host=${credentialModal.host} dbname=databricks_postgres user=${credentialModal.user} password=${credentialModal.token}"`}
                    style={{ fontFamily: "monospace", fontSize: "11px" }}
                  />
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      navigator.clipboard.writeText(
                        `psql "sslmode=require host=${credentialModal.host} dbname=databricks_postgres user=${credentialModal.user} password=${credentialModal.token}"`
                      );
                      showToast("Connection string copied to clipboard!");
                    }}
                  >
                    <Copy size={14} /> Copy
                  </button>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setCredentialModal(null)}>
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Role Modal */}
      {roleModal && (
        <div className="modal-overlay" onClick={() => setRoleModal(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Assign Database Role in Environment '{roleModal}'</h3>
              <button onClick={() => setRoleModal(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Identity (user email, group name, or service principal ID)</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. materials-managers, pharmacist@apexhealth.org, or a service principal ID"
                  value={roleIdentity}
                  onChange={(e) => setRoleIdentity(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Identity Type</label>
                <select
                  className="form-control"
                  value={roleType}
                  onChange={(e) => setRoleType(e.target.value)}
                >
                  <option value="USER">User</option>
                  <option value="GROUP">Group</option>
                  <option value="SERVICE_PRINCIPAL">Service Principal</option>
                </select>
              </div>
              <div className="form-group">
                <label>Permission Level</label>
                <select
                  className="form-control"
                  value={rolePermission}
                  onChange={(e) => setRolePermission(e.target.value)}
                >
                  <option value="CAN_CONNECT_AND_CREATE">Read/Write (CAN_CONNECT_AND_CREATE)</option>
                  <option value="CAN_SELECT">Read Only (SELECT)</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setRoleModal(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleAssignRole}>
                Execute Role Grant
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
