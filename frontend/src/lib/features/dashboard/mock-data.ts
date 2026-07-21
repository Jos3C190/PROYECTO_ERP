// MOCK DATA — reemplazar por llamadas reales cuando existan los módulos correspondientes.
// Todos los datos aquí son simulados. Ningún componente del dashboard hace fetch a endpoints de negocio.

// ---------- Types ----------

export interface KpiData {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  change: number; // percentage vs previous period
  sparkline: number[];
  icon: string; // SVG path data
}

export interface TimeSeriesPoint {
  date: string; // ISO date
  value: number;
}

export interface DistributionItem {
  label: string;
  value: number;
  color: string; // RGB triplet for dynamic theming
}

export interface ActivityItem {
  user: string;
  initials: string;
  action: string;
  resource: string;
  timeAgo: string;
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
    sparkline: [38, 40, 42, 41, 44, 45, 43, 46, 47],
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
    icon: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z',
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
  { label: 'Tecnología', value: 42, color: '0 112 243' },
  { label: 'Ventas', value: 28, color: '0 168 150' },
  { label: 'Recursos Humanos', value: 18, color: '237 151 39' },
  { label: 'Administración', value: 22, color: '99 102 241' },
  { label: 'Operaciones', value: 14, color: '239 68 68' },
];

// ---------- Activity feed (mock — coherent with real system actions) ----------

export const ACTIVITY: ActivityItem[] = [
  { user: 'Ana García', initials: 'AG', action: 'creó el usuario', resource: 'jperez', timeAgo: 'hace 5 min', status: 'success' },
  { user: 'Carlos López', initials: 'CL', action: 'asignó el rol', resource: 'ADMINISTRADOR a maria', timeAgo: 'hace 12 min', status: 'success' },
  { user: 'Sistema', initials: 'SY', action: 'registro intento de login fallido para', resource: 'unknown@e.com', timeAgo: 'hace 23 min', status: 'failure' },
  { user: 'María Fernández', initials: 'MF', action: 'editó el empleado', resource: 'EMP-0042', timeAgo: 'hace 1 h', status: 'success' },
  { user: 'Ana García', initials: 'AG', action: 'desactivó el usuario', resource: 'tempuser', timeAgo: 'hace 2 h', status: 'success' },
  { user: 'Carlos López', initials: 'CL', action: 'inició sesión', resource: '', timeAgo: 'hace 3 h', status: 'success' },
  { user: 'Sistema', initials: 'SY', action: 'creó el departamento', resource: 'Logística', timeAgo: 'ayer', status: 'success' },
  { user: 'María Fernández', initials: 'MF', action: 'revocó el rol', resource: 'RECURSOS_HUMANOS de bob', timeAgo: 'ayer', status: 'success' },
];

// ---------- Summary table (recent users) ----------

export const SUMMARY_ROWS: SummaryRow[] = [
  { name: 'Ana García', initials: 'AG', dept: 'Tecnología', status: 'active', createdAt: '21 Jul, 09:15' },
  { name: 'Carlos López', initials: 'CL', dept: 'Ventas', status: 'active', createdAt: '21 Jul, 08:42' },
  { name: 'María Fernández', initials: 'MF', dept: 'Recursos Humanos', status: 'active', createdAt: '20 Jul, 17:30' },
  { name: 'Juan Pérez', initials: 'JP', dept: 'Administración', status: 'active', createdAt: '20 Jul, 14:20' },
  { name: 'Laura Torres', initials: 'LT', dept: 'Operaciones', status: 'inactive', createdAt: '20 Jul, 11:05' },
  { name: 'Pedro Ramírez', initials: 'PR', dept: 'Tecnología', status: 'pending', createdAt: '19 Jul, 16:45' },
  { name: 'Sofía Castro', initials: 'SC', dept: 'Ventas', status: 'active', createdAt: '19 Jul, 10:30' },
  { name: 'Diego Morales', initials: 'DM', dept: 'Administración', status: 'locked', createdAt: '18 Jul, 15:10' },
  { name: 'Elena Vargas', initials: 'EV', dept: 'Recursos Humanos', status: 'active', createdAt: '18 Jul, 09:25' },
  { name: 'Roberto Díaz', initials: 'RD', dept: 'Operaciones', status: 'inactive', createdAt: '17 Jul, 14:00' },
];

// ---------- Team (for avatar group) ----------

export const TEAM: TeamMember[] = [
  { name: 'Ana García', initials: 'AG', role: 'Super Admin' },
  { name: 'Carlos López', initials: 'CL', role: 'Administrador' },
  { name: 'María Fernández', initials: 'MF', role: 'RRHH' },
  { name: 'Juan Pérez', initials: 'JP', role: 'Empleado' },
  { name: 'Laura Torres', initials: 'LT', role: 'Empleado' },
];

// ---------- Progress data ----------

export const ONBOARDING_PROGRESS = 72; // percentage