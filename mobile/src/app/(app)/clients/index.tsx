import { useState, useCallback, useRef } from 'react';
import {
  View, Text, FlatList, TextInput, StyleSheet,
  TouchableOpacity, ActivityIndicator, RefreshControl, Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useFocusEffect } from 'expo-router';
import { clientsService } from '@/services/clients.service';
import { Colors, Typography, Spacing, Radius, Shadow } from '@/constants/theme';
import type { Client } from '@/types/models';
import Screen from '@/components/layout/Screen';

export default function ClientsScreen() {
  const router = useRouter();

  const [clients, setClients] = useState<Client[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);

  const baseClientsRef = useRef<Client[]>([]);
  const basePageRef = useRef(1);
  const baseTotalPagesRef = useRef(1);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeQueryRef = useRef<string>('');

  const load = useCallback(async (
    pageNum: number,
    isRefresh = false,
  ) => {
    if (pageNum === 1) {
      isRefresh ? setRefreshing(true) : setLoading(true);
    } else {
      setLoadingMore(true);
    }
    setError(null);
    try {
      const res = await clientsService.list({ page: pageNum });
      setClients((prev) => pageNum === 1 ? res.results : [...prev, ...res.results]);
      setTotalPages(res.total_pages);
      setPage(pageNum);

      if (pageNum === 1) {
        baseClientsRef.current = res.results;
      } else {
        baseClientsRef.current = [...baseClientsRef.current, ...res.results];
      }
      basePageRef.current = pageNum;
      baseTotalPagesRef.current = res.total_pages;
    } catch {
      setError('No se pudieron cargar los clientes.');
    } finally {
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      setSearch('');
      activeQueryRef.current = '';
      if (debounceRef.current) clearTimeout(debounceRef.current);
      load(1);
    }, [load]),
  );

  const handleRefresh = () => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    activeQueryRef.current = '';
    setSearch('');
    load(1, true);
  };

  const handleLoadMore = () => {
    if (!loadingMore && !search && page < totalPages) {
      load(page + 1);
    }
  };

  const handleSearchChange = useCallback((text: string) => {
    setSearch(text);
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!text.trim()) {
      setClients(baseClientsRef.current);
      setPage(basePageRef.current);
      setTotalPages(baseTotalPagesRef.current);
      setSearchLoading(false);
      activeQueryRef.current = '';
      return;
    }

    const q = text.toLowerCase();
    const local = baseClientsRef.current.filter((c) =>
      [c.name, c.phone].some((f) => f?.toLowerCase().includes(q))
    );

    if (local.length > 0) {
      setClients(local);
      setSearchLoading(false);
      return;
    }

    activeQueryRef.current = text;
    debounceRef.current = setTimeout(async () => {
      if (activeQueryRef.current !== text) return;
      setSearchLoading(true);
      try {
        const res = await clientsService.list({ page: 1, search: text });
        if (activeQueryRef.current !== text) return;
        setClients(res.results);
      } catch {
        Alert.alert('Error', 'No se pudieron buscar clientes.');
        setClients([]);
      } finally {
        if (activeQueryRef.current === text) setSearchLoading(false);
      }
    }, 300);
  }, []);

  const renderClient = ({ item }: { item: Client }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/(app)/clients/${item.id}`)}
      activeOpacity={0.8}
      accessibilityRole="button"
      accessibilityLabel={item.name}
    >
      <View style={styles.cardRow}>
        <Text style={styles.clientName} numberOfLines={1}>{item.name}</Text>
        <View style={styles.projectsBadge}>
          <Text style={styles.projectsBadgeText}>
            {item.projects_count} {item.projects_count === 1 ? 'proyecto' : 'proyectos'}
          </Text>
        </View>
      </View>
      {item.phone ? (
        <Text style={styles.clientPhone} numberOfLines={1}>{item.phone}</Text>
      ) : null}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <Screen>
        <View style={styles.center}>
          <ActivityIndicator color={Colors.primary} size="large" />
        </View>
      </Screen>
    );
  }

  if (error && clients.length === 0) {
    return (
      <Screen>
        <View style={styles.center}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={() => load(1)}>
            <Text style={styles.retryText}>Reintentar</Text>
          </TouchableOpacity>
        </View>
      </Screen>
    );
  }

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.title}>Clientes</Text>
        <TouchableOpacity
          style={styles.newBtn}
          onPress={() => router.push('/(app)/clients/create')}
          activeOpacity={0.8}
          accessibilityRole="button"
          accessibilityLabel="Nuevo cliente"
        >
          <Text style={styles.newBtnText}>+ Nuevo</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Buscar cliente..."
          placeholderTextColor={Colors.textMuted}
          value={search}
          onChangeText={handleSearchChange}
          returnKeyType="search"
          clearButtonMode="while-editing"
          accessibilityLabel="Buscar cliente"
        />
        {searchLoading ? (
          <ActivityIndicator color={Colors.primary} size="small" style={styles.searchSpinner} />
        ) : null}
      </View>

      <FlatList
        data={clients}
        keyExtractor={(item) => String(item.id)}
        renderItem={renderClient}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={Colors.primary}
          />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.3}
        ListFooterComponent={
          loadingMore
            ? <ActivityIndicator color={Colors.primary} style={styles.footerLoader} />
            : null
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>
              {search ? 'Sin resultados para la búsqueda.' : 'No hay clientes registrados.'}
            </Text>
          </View>
        }
      />
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
  title: { fontSize: Typography.size.xxl, fontWeight: Typography.weight.bold, color: Colors.text },
  newBtn: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.md,
    backgroundColor: Colors.primary,
  },
  newBtnText: { fontSize: Typography.size.sm, fontWeight: Typography.weight.semibold, color: Colors.white },
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
  listContent: { paddingHorizontal: Spacing.lg, paddingBottom: Spacing.xxl, gap: Spacing.sm },
  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 4,
    ...Shadow.sm,
  },
  cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  clientName: {
    flex: 1,
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.semibold,
    color: Colors.text,
    marginRight: Spacing.sm,
  },
  projectsBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: Radius.pill,
    backgroundColor: Colors.primaryLight,
  },
  projectsBadgeText: { fontSize: Typography.size.xs, fontWeight: Typography.weight.medium, color: Colors.primary },
  clientPhone: { fontSize: Typography.size.sm, color: Colors.textMuted },
  footerLoader: { paddingVertical: Spacing.lg },
  empty: { alignItems: 'center', paddingTop: Spacing.xl },
  emptyText: { fontSize: Typography.size.md, color: Colors.textMuted },
  errorText: { fontSize: Typography.size.md, color: Colors.error },
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
