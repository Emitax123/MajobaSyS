import { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  ActivityIndicator, ScrollView, Alert,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { clientsService } from '@/services/clients.service';
import { Colors, Typography, Spacing, Radius, Shadow } from '@/constants/theme';
import type { Client } from '@/types/models';
import Screen from '@/components/layout/Screen';

export default function ClientDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const clientId = Number(id);
    if (!clientId) return;

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
            Desde {new Date(client.created_at).toLocaleDateString('es-AR', {
              year: 'numeric', month: 'short', day: 'numeric',
            })}
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

const styles = StyleSheet.create({
  scroll: { flex: 1 },
  content: { padding: Spacing.lg, gap: Spacing.md },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: Spacing.md,
  },

  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: Spacing.sm,
    ...Shadow.sm,
  },
  clientName: {
    fontSize: Typography.size.xxl,
    fontWeight: Typography.weight.bold,
    color: Colors.text,
  },
  fieldValue: {
    fontSize: Typography.size.md,
    color: Colors.textMuted,
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
    backgroundColor: Colors.primaryLight,
  },
  projectsBadgeText: {
    fontSize: Typography.size.xs,
    fontWeight: Typography.weight.medium,
    color: Colors.primary,
  },
  createdAt: {
    fontSize: Typography.size.xs,
    color: Colors.textDisabled,
  },

  actions: { gap: Spacing.sm },
  btnPrimary: {
    backgroundColor: Colors.primary,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
  },
  btnPrimaryText: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: Colors.white,
  },
  btnSecondary: {
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  btnSecondaryText: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: Colors.text,
  },

  retryBtn: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.md,
    backgroundColor: Colors.bgElevated,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  retryText: { fontSize: Typography.size.sm, color: Colors.text },
  errorText: { fontSize: Typography.size.md, color: Colors.error },

  btnDanger: {
    backgroundColor: Colors.error,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
  },
  btnDisabled: { opacity: 0.6 },
  btnDangerText: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: Colors.white,
  },
});
