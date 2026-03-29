import { useMemo, useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  ActivityIndicator, ScrollView, Alert,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { projectsService } from '@/services/projects.service';
import { useColors, Typography, Spacing, Radius, Shadow } from '@/constants/theme';
import type { AppColors } from '@/constants/theme';
import type { Project } from '@/types/models';
import Screen from '@/components/layout/Screen';

export default function ProjectDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const Colors = useColors();
  const styles = useMemo(() => createStyles(Colors), [Colors]);

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const projectId = Number(id);
    if (!Number.isFinite(projectId) || projectId <= 0) {
      setError('ID de proyecto inválido.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    projectsService.get(projectId)
      .then((data) => setProject(data))
      .catch(() => setError('No se pudo cargar el proyecto.'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = () => {
    if (!project) return;
    Alert.alert(
      'Eliminar proyecto',
      `¿Estás seguro de que querés eliminar "${project.name}"? Esta acción no se puede deshacer.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            setDeleting(true);
            try {
              await projectsService.remove(Number(id));
              router.back();
            } catch {
              Alert.alert('Error', 'No se pudo eliminar el proyecto.');
              setDeleting(false);
            }
          },
        },
      ],
    );
  };

  const formatDate = (dateStr: string) => {
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      const [y, m, d] = parts.map(Number);
      if (Number.isFinite(y) && Number.isFinite(m) && Number.isFinite(d)) {
        return new Date(y, m - 1, d).toLocaleDateString('es-AR', {
          year: 'numeric', month: 'short', day: 'numeric',
        });
      }
    }
    return new Date(dateStr).toLocaleDateString('es-AR', {
      year: 'numeric', month: 'short', day: 'numeric',
    });
  };

  if (loading) {
    return (
      <Screen>
        <View style={styles.center}>
          <ActivityIndicator color={Colors.primary} size="large" />
        </View>
      </Screen>
    );
  }

  if (error || !project) {
    return (
      <Screen>
        <View style={styles.center}>
          <Text style={styles.errorText}>{error ?? 'Proyecto no encontrado.'}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={() => router.back()}>
            <Text style={styles.retryText}>Volver</Text>
          </TouchableOpacity>
        </View>
      </Screen>
    );
  }

  return (
    <Screen>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>

        {/* Back */}
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn} activeOpacity={0.7}>
          <Text style={styles.backText}>← Volver</Text>
        </TouchableOpacity>

        {/* Tarjeta principal */}
        <View style={styles.card}>
          {/* Nombre + badge */}
          <View style={styles.cardHeader}>
            <Text style={styles.projectName}>{project.name}</Text>
            <View style={[styles.badge, project.is_active ? styles.badgeActive : styles.badgeInactive]}>
              <Text style={[styles.badgeText, project.is_active ? styles.badgeTextActive : styles.badgeTextInactive]}>
                {project.is_active ? 'Activo' : 'Inactivo'}
              </Text>
            </View>
          </View>

          {/* Cliente */}
          {project.client_name ? (
            <View style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>Cliente</Text>
              <Text style={styles.fieldValue}>{project.client_name}</Text>
            </View>
          ) : null}

          <View style={styles.divider} />

          {/* Descripción */}
          {project.description ? (
            <View style={styles.fieldBlock}>
              <Text style={styles.fieldLabel}>Descripción</Text>
              <Text style={styles.fieldValueBlock}>{project.description}</Text>
            </View>
          ) : null}

          {/* Ubicación */}
          {project.location ? (
            <View style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>Ubicación</Text>
              <Text style={styles.fieldValue} numberOfLines={2}>{project.location}</Text>
            </View>
          ) : null}

          {/* Fechas */}
          <View style={styles.fieldRow}>
            <Text style={styles.fieldLabel}>Inicio</Text>
            <Text style={styles.fieldValue}>{formatDate(project.start_date)}</Text>
          </View>

          {project.end_date ? (
            <View style={styles.fieldRow}>
              <Text style={styles.fieldLabel}>Fin</Text>
              <Text style={styles.fieldValue}>{formatDate(project.end_date)}</Text>
            </View>
          ) : null}

          <View style={styles.divider} />

          {/* Creado */}
          <Text style={styles.createdAt}>Creado el {formatDate(project.created_at)}</Text>
        </View>

        {/* Acciones */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.btnSecondary, deleting && styles.btnDisabled]}
            onPress={() => router.push(`/(app)/projects/edit/${project.id}`)}
            disabled={deleting}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel="Editar proyecto"
          >
            <Text style={styles.btnSecondaryText}>Editar proyecto</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.btnDanger, deleting && styles.btnDisabled]}
            onPress={handleDelete}
            disabled={deleting}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel="Eliminar proyecto"
          >
            {deleting
              ? <ActivityIndicator color={Colors.white} />
              : <Text style={styles.btnDangerText}>Eliminar proyecto</Text>}
          </TouchableOpacity>
        </View>

      </ScrollView>
    </Screen>
  );
}

const createStyles = (c: AppColors) => StyleSheet.create({
  scroll: { flex: 1 },
  content: { padding: Spacing.lg, gap: Spacing.md },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: Spacing.md },

  backBtn: { alignSelf: 'flex-start' },
  backText: { fontSize: Typography.size.sm, color: c.primary, fontWeight: Typography.weight.medium },

  card: {
    backgroundColor: c.bgCard,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: c.border,
    gap: Spacing.sm,
    ...Shadow.sm,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: Spacing.sm,
  },
  projectName: {
    flex: 1,
    fontSize: Typography.size.xxl,
    fontWeight: Typography.weight.bold,
    color: c.text,
  },

  badge: { paddingHorizontal: Spacing.sm, paddingVertical: 3, borderRadius: Radius.pill, marginTop: 4 },
  badgeActive: { backgroundColor: c.successLight },
  badgeInactive: { backgroundColor: c.bgElevated },
  badgeText: { fontSize: Typography.size.xs, fontWeight: Typography.weight.medium },
  badgeTextActive: { color: c.success },
  badgeTextInactive: { color: c.textMuted },

  divider: { height: 1, backgroundColor: c.border, marginVertical: Spacing.xs },

  fieldRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: Spacing.sm,
  },
  fieldBlock: { gap: 4 },
  fieldLabel: {
    fontSize: Typography.size.sm,
    color: c.textMuted,
    fontWeight: Typography.weight.medium,
    flexShrink: 0,
  },
  fieldValue: {
    flex: 1,
    fontSize: Typography.size.sm,
    color: c.text,
    textAlign: 'right',
  },
  fieldValueBlock: {
    fontSize: Typography.size.sm,
    color: c.text,
    lineHeight: Typography.size.sm * 1.5,
  },

  createdAt: { fontSize: Typography.size.xs, color: c.textDisabled },

  actions: { gap: Spacing.sm },

  btnSecondary: {
    backgroundColor: c.bgCard,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: c.border,
  },
  btnSecondaryText: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: c.text,
  },

  btnDanger: {
    backgroundColor: c.error,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
  },
  btnDisabled: { opacity: 0.6 },
  btnDangerText: { fontSize: Typography.size.md, fontWeight: Typography.weight.semibold, color: c.white },

  retryBtn: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.md,
    backgroundColor: c.bgElevated,
    borderWidth: 1,
    borderColor: c.border,
  },
  retryText: { fontSize: Typography.size.sm, color: c.text },
  errorText: { fontSize: Typography.size.md, color: c.error },
});
