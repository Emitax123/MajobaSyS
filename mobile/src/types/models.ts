// ============================================================================
// Tipos de modelos — espejo de los modelos Django del backend
// ============================================================================

export type AccLevel =
  | 'principiante'
  | 'intermedio'
  | 'avanzado'
  | 'experto'
  | 'maestro';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  profession?: string;
  direction?: string;
  is_staff: boolean;
  is_active: boolean;
}

export interface ManagerData {
  id: number;
  points: number;
  acc_level: AccLevel;
  notifications: number;
  progress_percentage: number;
  points_for_next_level: number;
  next_level_display: string;
}

export interface Client {
  id: number;
  name: string;
  phone?: string;
  projects_count: number;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  location?: string;
  start_date: string;
  end_date?: string | null;
  is_active: boolean;
  client?: number;
  client_name?: string;
  created_at: string;
}

export interface Notification {
  id: number;
  message: string;
  description?: string;
  is_read: boolean;
  created_at: string;
  time_elapsed: string;
}
