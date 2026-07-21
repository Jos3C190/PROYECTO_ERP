// MOCK DATA — reemplazar por llamadas reales cuando existan los módulos correspondientes.
// Todos los datos aquí son simulados. Ningún componente del dashboard hace fetch a endpoints de negocio.

// ---------- Pool unificado de usuarios mock (usado en todos los widgets) ----------

export interface MockUser {
  name: string;
  initials: string;
  dept: string;
}

export const USERS: MockUser[] = [
  { name: 'Ana García', initials: 'AG', dept: 'Tecnología' },
  { name: 'Carlos López', initials: 'CL', dept: 'Ventas' },
  { name: 'María Fernández', initials: 'MF', dept: 'Recursos Humanos' },
  { name: 'Juan Pérez', initials: 'JP', dept: 'Administración' },
  { name: 'Laura Torres', initials: 'LT', dept: 'Operaciones' },
  { name: 'Pedro Ramírez', initials: 'PR', dept: 'Tecnología' },
  { name: 'Sofía Castro', initials: 'SC', dept: 'Ventas' },
  { name: 'Diego Morales', initials: 'DM', dept: 'Administración' },
  { name: 'Elena Vargas', initials: 'EV', dept: 'Recursos Humanos' },
  { name: 'Roberto Díaz', initials: 'RD', dept: 'Operaciones' },
];

// ---------- Types ----------

export interface KpiData {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  change: number;
  sparkline: number[];
  icon: string;
}

export interface TimeSeriesPoint {
  date: string;
  value: number;
}

export interface DistributionItem {
  label: string;
  value: number;
}

export interface ActivityItem {
  user: string;
  initials: string;
  isSystem: boolean;
  action: string;
  resource: string;
  minutesAgo: number;
  status: 'success' | 'failure';
}

export interface SummaryRow {
  name: string;
  initials: string;
  dept: string;
  status: 'active' | 'inactive' | 'pending' | 'locked';
  createdAt: string;
}

export interface TeamMember {
  name: string;
  initials: string;
  role: string;
}

// ---------- KPIs ----------

export const KPIS: KpiData[] = [
  {
    label: 'Usuarios activos',
    value: 47,
    change: 12.5,
    sparkline: [38, 39, 41, 40, 42, 44, 43, 45, 47],
    icon: 'M17 20h5v-2a4 4 0 0 0-3-3.87M9 20H4v-2a4 4 0 0 1 3-3.87m6-2a4 4 0 1 0-8 0 4 4 0 0 0 8 0z',
  },
  {
    label: 'Empleados totales',
    value: 1284,
    change: 3.2,
    sparkline: [1220, 1230, 1245, 1250, 1260, 1270, 1275, 1280, 1284],
    icon: 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM12 14a7 7 0 0 0-7 7h14a7 7 0 0 0-7-7z',
  },
  {
    label: 'Eventos hoy',
    value: 342,
    change: -8.1,
    sparkline: [380, 375, 370, 365, 360, 355, 350, 345, 342],
    icon: 'M13 2L3 14h7l-1 8 10-12h-7l1-8z',
  },
  {
    label: 'Roles configurados',
    value: 4,
    change: 0,
    sparkline: [4, 4, 4, 4, 4, 4, 4, 4, 4],
    icon: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  },
];

// ---------- Time series for main chart ----------

function generateSeries(days: number, base: number, trend: number, noise: number): TimeSeriesPoint[] {
  const points: TimeSeriesPoint[] = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const t = (days - i) / days;
    const n = (Math.sin(i * 0.7) + Math.cos(i * 1.3)) * noise;
    points.push({
      date: d.toISOString().split('T')[0],
      value: Math.round(base + trend * t * base + n),
    });
  }
  return points;
}

export const SERIES_7D = generateSeries(7, 380, 0.15, 15);
export const SERIES_30D = generateSeries(30, 350, 0.12, 25);
export const SERIES_90D = generateSeries(90, 320, 0.18, 30);

// ---------- Distribution (employees by department) ----------

export const DEPT_DISTRIBUTION: DistributionItem[] = [
  { label: 'Tecnología', value: 42 },
  { label: 'Ventas', value: 28 },
  { label: 'Recursos Humanos', value: 18 },
  { label: 'Administración', value: 22 },
  { label: 'Operaciones', value: 14 },
];

// ---------- Activity feed (mock — variado, sin repeticiones consecutivas) ----------

export const ACTIVITY: ActivityItem[] = [
  { user: 'Ana García', initials: 'AG', isSystem: false, action: 'creó el usuario', resource: 'jperez', minutesAgo: 5, status: 'success' },
  { user: 'Carlos López', initials: 'CL', isSystem: false, action: 'asignó el rol', resource: 'ADMINISTRADOR a mf', minutesAgo: 12, status: 'success' },
  { user: 'Sistema', initials: 'SY', isSystem: true, action: 'registró intento de login fallido para', resource: 'unknown@e.com', minutesAgo: 23, status: 'failure' },
  { user: 'María Fernández', initials: 'MF', isSystem: false, action: 'editó el empleado', resource: 'EMP-0042', minutesAgo: 47, status: 'success' },
  { user: 'Ana García', initials: 'AG', isSystem: false, action: 'desactivó el usuario', resource: 'tempuser', minutesAgo: 95, status: 'success' },
  { user: 'Carlos López', initials: 'CL', isSystem: false, action: 'inició sesión', resource: '', minutesAgo: 180, status: 'success' },
  { user: 'Sistema', initials: 'SY', isSystem: true, action: 'creó el departamento', resource: 'Logística', minutesAgo: 320, status: 'success' },
  { user: 'María Fernández', initials: 'MF', isSystem: false, action: 'revocó el rol', resource: 'RRHH de bob', minutesAgo: 480, status: 'success' },
  { user: 'Juan Pérez', initials: 'JP', isSystem: false, action: 'reseteó la contraseña de', resource: 'ltorres', minutesAgo: 720, status: 'success' },
  { user: 'Sistema', initials: 'SY', isSystem: true, action: 'desbloqueó la cuenta de', resource: 'dmorales', minutesAgo: 900, status: 'success' },
];

function formatTimeAgo(minutes: number): string {
  if (minutes < 1) return 'ahora';
  if (minutes < 60) return `hace ${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `hace ${hours}h`;
  return `hace ${Math.floor(hours / 24)}d`;
}

export const ACTIVITY_FORMATTED = ACTIVITY.map(a => ({ ...a, timeAgo: formatTimeAgo(a.minutesAgo) }));

// ---------- Summary table (uses same user pool) ----------

export const SUMMARY_ROWS: SummaryRow[] = USERS.slice(0, 10).map((u, i) => ({
  name: u.name,
  initials: u.initials,
  dept: u.dept,
  status: (['active', 'active', 'active', 'active', 'inactive', 'pending', 'active', 'locked', 'active', 'inactive'] as const)[i],
  createdAt: `${20 - Math.floor(i / 3)} Jul, ${['09:15', '08:42', '17:30', '14:20', '11:05', '16:45', '10:30', '15:10', '09:25', '14:00'][i]}`,
}));

// ---------- Team (uses same user pool) ----------

export const TEAM: TeamMember[] = [
  { name: 'Ana García', initials: 'AG', role: 'Super Admin' },
  { name: 'Carlos López', initials: 'CL', role: 'Administrador' },
  { name: 'María Fernández', initials: 'MF', role: 'RRHH' },
  { name: 'Juan Pérez', initials: 'JP', role: 'Empleado' },
  { name: 'Laura Torres', initials: 'LT', role: 'Empleado' },
];

// ---------- Progress data ----------

export const ONBOARDING_PROGRESS = 72;