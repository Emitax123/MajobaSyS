import apiClient from './api';
import { API_ENDPOINTS } from '@/constants/api';
import type { PaginatedResponse } from '@/types/api.types';
import type { Project } from '@/types/models';

export const projectsService = {
  async list(params?: { page?: number; page_size?: number; search?: string; is_active?: boolean; client?: number }): Promise<PaginatedResponse<Project>> {
    const { data } = await apiClient.get<PaginatedResponse<Project>>(
      API_ENDPOINTS.projects,
      { params },
    );
    return data;
  },

  async get(id: number): Promise<Project> {
    const { data } = await apiClient.get<Project>(API_ENDPOINTS.project(id));
    return data;
  },

  async create(payload: Partial<Project> & { new_client_name?: string; new_client_phone?: string }): Promise<Project> {
    const { data } = await apiClient.post<Project>(API_ENDPOINTS.projects, payload);
    return data;
  },

  async update(id: number, payload: Partial<Project>): Promise<Project> {
    const { data } = await apiClient.patch<Project>(API_ENDPOINTS.project(id), payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.project(id));
  },
};
