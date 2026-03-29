import { useMemo, useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  ActivityIndicator, ScrollView, Alert,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { clientsService } from '@/services/clients.service';
import { useColors, Typography, Spacing, Radius, Shadow } from '@/constants/theme';
import type { AppColors } from '@/constants/theme';
import type { Client } from '@/types/models';
import Screen from '@/components/layout/Screen';

export default function ClientDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const Colors = useColors();
  const styles = useMemo(() => createStyles(Colors), [Colors]);

  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const clientId = Number(id);
    if (!Number.isFinite(clientId) || clientId <= 0) {
      setError('Cliente inválido.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    clientsService.get(clientId)
      .then((data) => setClient(data))
      .catch(() => setError('No se pudo cargar el cliente.'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = () => {
    if (!client) return;
    Alert.alert(
      'Eliminar cliente',
      '¿Estás seguro? Esta acción eliminará todos los proyectos asociados y no se puede deshacer.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            setDeleting(true);
            try {
              await clientsService.remove(Number(id));
              router.replace('/(app)/clients');
            } catch {
              Alert.alert('Error', 'No se pudo eliminar el cliente.');
              setDeleting(false);
            }
          },
        },
      ],
    );
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

  if (error || !client) {
    return (
      <Screen>
        <View style={styles.center}>
          <Text style={styles.errorText}>{error ?? 'Cliente no encontrado.'}</Text>
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
      {/* Tarjeta principal */}
      <View style={styles.card}>
        <Text style={styles.clientName}>{client.name}</Text>
        {client.phone ? (
          <Text style={styles.fieldValue}>{client.phone}</Text>
        ) : null}
        <View style={styles.metaRow}>
          <View style={styles.projectsBadge}>
            <Text style={styles.projectsBadgeText}>
              {client.projects_count} {client.projects_count === 1 ? 'proyecto' : 'proyectos'}
            </Text>
          </View>
          <Text style={styles.createdAt}>
            Desde {(() => {
              const parts = client.created_at.split('-');
              if (parts.length >= 3) {
                const [y, m, d] = parts.map((s: string) => Number(s));
                if (Number.isFinite(y) && Number.isFinite(m) && Number.isFinite(d)) {
                  return new Date(y, m - 1, d).toLocaleDateString('es-AR', {
                    year: 'numeric', month: 'short', day: 'numeric',
                  });
                }
              }
              return new Date(client.created_at).toLocaleDateString('es-AR', {
                year: 'numeric', month: 'short', day: 'numeric',
              });
            })()}
          </Text>
        </View>
      </View>

      {/* Acciones */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.btnPrimary, deleting && styles.btnDisabled]}
          onPress={() => router.push({
            pathname: '/(app)/projects',
            params: { clientId: client.id, clientName: client.name },
          })}
          activeOpacity={0.8}
          disabled={deleting}
          accessibilityRole="button"
          accessibilityLabel="Ver proyectos de este cliente"
        >
          <Text style={styles.btnPrimaryText}>Ver proyectos</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btnSecondary, deleting && styles.btnDisabled]}
          onPress={() => router.push(`/(app)/clients/edit/${client.id}`)}
          activeOpacity={0.8}
          disabled={deleting}
          accessibilityRole="button"
          accessibilityLabel="Editar cliente"
        >
          <Text style={styles.btnSecondaryText}>Editar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btnSecondary, deleting && styles.btnDisabled]}
          onPress={() => router.push({
            pathname: '/(app)/projects/create',
            params: { client: client.id, client_name: client.name },
          })}
          activeOpacity={0.8}
          disabled={deleting}
          accessibilityRole="button"
          accessibilityLabel="Crear proyecto para este cliente"
        >
          <Text style={styles.btnSecondaryText}>Nuevo proyecto</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btnDanger, deleting && styles.btnDisabled]}
          onPress={handleDelete}
          disabled={deleting}
          activeOpacity={0.8}
          accessibilityRole="button"
          accessibilityLabel="Eliminar cliente"
        >
          {deleting
            ? <ActivityIndicator color={Colors.white} />
            : <Text style={styles.btnDangerText}>Eliminar cliente</Text>}
        </TouchableOpacity>
      </View>
      </ScrollView>
    </Screen>
  );
}

const createStyles = (c: AppColors) => StyleSheet.create({
  scroll: { flex: 1 },
  content: { padding: Spacing.lg, gap: Spacing.md },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: Spacing.md,
  },

  card: {
    backgroundColor: c.bgCard,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: c.border,
    gap: Spacing.sm,
    ...Shadow.sm,
  },
  clientName: {
    fontSize: Typography.size.xxl,
    fontWeight: Typography.weight.bold,
    color: c.text,
  },
  fieldValue: {
    fontSize: Typography.size.md,
    color: c.textMuted,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.xs,
  },
  projectsBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: Radius.pill,
    backgroundColor: c.primaryLight,
  },
  projectsBadgeText: {
    fontSize: Typography.size.xs,
    fontWeight: Typography.weight.medium,
    color: c.primary,
  },
  createdAt: {
    fontSize: Typography.size.xs,
    color: c.textDisabled,
  },

  actions: { gap: Spacing.sm },
  btnPrimary: {
    backgroundColor: c.primary,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
  },
  btnPrimaryText: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: c.white,
  },
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

  btnDanger: {
    backgroundColor: c.error,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
  },
  btnDisabled: { opacity: 0.6 },
  btnDangerText: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: c.white,
  },
});
