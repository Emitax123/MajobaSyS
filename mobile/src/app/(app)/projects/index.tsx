import { useState, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  ActivityIndicator, FlatList, RefreshControl, TextInput, Alert,
} from 'react-native';
import { useFocusEffect, useLocalSearchParams, useRouter } from 'expo-router';
import { projectsService } from '@/services/projects.service';
import { Colors, Typography, Spacing, Radius, Shadow } from '@/constants/theme';
import type { Project } from '@/types/models';
import Screen from '@/components/layout/Screen';

function parseClientId(raw: string | string[] | undefined): number | undefined {
  const str = Array.isArray(raw) ? raw[0] : raw;
  const n = Number(str);
  return Number.isFinite(n) && n > 0 ? n : undefined;
}

export default function ProjectsScreen() {
  const params = useLocalSearchParams<{ clientId?: string | string[]; clientName?: string | string[] }>();
  const router = useRouter();

  const clientId = parseClientId(params.clientId);
  const clientName = Array.isArray(params.clientName) ? params.clientName[0] : params.clientName;

  const [baseProjects, setBaseProjects] = useState<Project[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeQueryRef = useRef<string>('');

  const fetchProjects = useCallback((signal?: { cancelled: boolean }) => {
    return projectsService
      .list({ ...(clientId ? { client: clientId } : {}), page_size: 100 })
      .then((res) => {
        if (!signal?.cancelled) {
          setBaseProjects(res.results);
          setProjects(res.results);
        }
      })
      .catch(() => {
        if (!signal?.cancelled) setError('No se pudieron cargar los proyectos.');
      });
  }, [clientId]);

  useFocusEffect(
    useCallback(() => {
      const signal = { cancelled: false };
      setLoading(true);
      setError(null);
      setSearchQuery('');
      fetchProjects(signal).finally(() => {
        if (!signal.cancelled) setLoading(false);
      });
      return () => {
        signal.cancelled = true;
        if (debounceRef.current) clearTimeout(debounceRef.current);
        activeQueryRef.current = '';
      };
    }, [fetchProjects]),
  );

  const onRefresh = useCallback(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    activeQueryRef.current = '';
    setRefreshing(true);
    setSearchQuery('');
    fetchProjects().finally(() => setRefreshing(false));
  }, [fetchProjects]);

  const handleSearchChange = useCallback((text: string) => {
    setSearchQuery(text);

    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!text.trim()) {
      setProjects(baseProjects);
      setSearchLoading(false);
      return;
    }

    const q = text.toLowerCase();
    const local = baseProjects.filter((p) =>
      [p.name, p.description, p.location].some((f) => f?.toLowerCase().includes(q))
    );

    if (local.length > 0) {
      setProjects(local);
      setSearchLoading(false);
      return;
    }

    // No local matches — debounce API fallback
    activeQueryRef.current = text;
    debounceRef.current = setTimeout(async () => {
      if (activeQueryRef.current !== text) return; // stale guard
      setSearchLoading(true);
      try {
        const res = await projectsService.list({
          search: text,
          page_size: 100,
          ...(clientId ? { client: clientId } : {}),
        });
        if (activeQueryRef.current !== text) return; // stale guard
        setProjects(res.results);
      } catch {
        Alert.alert('Error', 'No se pudieron buscar proyectos.');
        setProjects([]);
      } finally {
        if (activeQueryRef.current === text) setSearchLoading(false);
      }
    }, 300);
  }, [baseProjects, clientId]);

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('es-AR', {
      year: 'numeric', month: 'short', day: 'numeric',
    });

  const renderItem = useCallback(({ item }: { item: Project }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/(app)/projects/${item.id}`)}
      activeOpacity={0.8}
      accessibilityRole="button"
      accessibilityLabel={item.name}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.projectName} numberOfLines={1}>{item.name}</Text>
        <View style={[styles.badge, item.is_active ? styles.badgeActive : styles.badgeInactive]}>
          <Text style={[styles.badgeText, item.is_active ? styles.badgeTextActive : styles.badgeTextInactive]}>
            {item.is_active ? 'Activo' : 'Inactivo'}
          </Text>
        </View>
      </View>
      {item.location ? (
        <Text style={styles.location} numberOfLines={1}>{item.location}</Text>
      ) : null}
      <Text style={styles.date}>Inicio: {formatDate(item.start_date)}</Text>
    </TouchableOpacity>
  ), [router]);

  return (
    <Screen>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <TouchableOpacity onPress={() => router.back()} activeOpacity={0.7}>
            <Text style={styles.backText}>←</Text>
          </TouchableOpacity>
          <Text style={styles.title} numberOfLines={1}>
            {clientName ?? 'Proyectos'}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.newBtn}
          onPress={() => router.push({
            pathname: '/(app)/projects/create',
            params: clientId ? { client: clientId, client_name: clientName } : {},
          })}
          activeOpacity={0.8}
          accessibilityRole="button"
          accessibilityLabel="Nuevo proyecto"
        >
          <Text style={styles.newBtnText}>+ Nuevo</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Buscar proyecto..."
          placeholderTextColor={Colors.textMuted}
          value={searchQuery}
          onChangeText={handleSearchChange}
          returnKeyType="search"
          clearButtonMode="while-editing"
          accessibilityLabel="Buscar proyecto"
        />
        {searchLoading ? (
          <ActivityIndicator
            color={Colors.primary}
            size="small"
            style={styles.searchSpinner}
          />
        ) : null}
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color={Colors.primary} size="large" />
        </View>
      ) : error ? (
        <View style={styles.center}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.retryBtn}
            onPress={() => {
              setLoading(true);
              setError(null);
              fetchProjects().finally(() => setLoading(false));
            }}
          >
            <Text style={styles.retryText}>Reintentar</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={projects}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={Colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={styles.emptyText}>
                {searchQuery ? 'Sin resultados para la búsqueda.' : 'No hay proyectos para este cliente.'}
              </Text>
            </View>
          }
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: Spacing.md },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.sm,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    flex: 1,
    marginRight: Spacing.sm,
  },
  backText: {
    fontSize: Typography.size.xl,
    color: Colors.primary,
    fontWeight: Typography.weight.medium,
  },
  title: {
    fontSize: Typography.size.xl,
    fontWeight: Typography.weight.bold,
    color: Colors.text,
    flex: 1,
  },
  newBtn: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.md,
    backgroundColor: Colors.primary,
  },
  newBtnText: {
    fontSize: Typography.size.sm,
    fontWeight: Typography.weight.semibold,
    color: Colors.white,
  },

  searchContainer: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  searchInput: {
    flex: 1,
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    fontSize: Typography.size.md,
    color: Colors.text,
  },
  searchSpinner: { marginLeft: Spacing.xs },

  listContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xxl,
    gap: Spacing.sm,
    flexGrow: 1,
  },

  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 4,
    ...Shadow.sm,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  projectName: {
    flex: 1,
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: Colors.text,
  },
  badge: { paddingHorizontal: Spacing.sm, paddingVertical: 2, borderRadius: Radius.pill },
  badgeActive: { backgroundColor: Colors.successLight },
  badgeInactive: { backgroundColor: Colors.bgElevated },
  badgeText: { fontSize: Typography.size.xs, fontWeight: Typography.weight.medium },
  badgeTextActive: { color: Colors.success },
  badgeTextInactive: { color: Colors.textMuted },

  location: { fontSize: Typography.size.sm, color: Colors.textMuted },
  date: { fontSize: Typography.size.xs, color: Colors.textDisabled },

  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: Spacing.xl },
  emptyText: { fontSize: Typography.size.md, color: Colors.textMuted },

  errorText: { fontSize: Typography.size.md, color: Colors.error, textAlign: 'center' },
  retryBtn: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm,
    borderRadius: Radius.md,
    backgroundColor: Colors.bgElevated,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  retryText: { fontSize: Typography.size.sm, color: Colors.text },
});
