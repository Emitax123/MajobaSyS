import { Alert, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Radius, Shadow, Spacing, Typography } from '@/constants/theme';
import Screen from '@/components/layout/Screen';
import { useAuthStore } from '@/stores/auth.store';

const ICON_SIZE = 20;

export default function ProfileScreen() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const isLoading = useAuthStore((s) => s.isLoading);

  const handleLogout = () => {
    Alert.alert(
      'Cerrar sesión',
      '¿Estás seguro de que querés cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar sesión',
          style: 'destructive',
          onPress: () => { void logout(); },
        },
      ],
    );
  };

  return (
    <Screen>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.eyebrow}>Perfil</Text>
          <Text style={styles.fullName}>{user?.full_name ?? '—'}</Text>
          <Text style={styles.username}>@{user?.username ?? '—'}</Text>
        </View>

        {/* Cuenta section */}
        <Text style={styles.sectionLabel}>Cuenta</Text>
        <View style={styles.card}>
          <InfoRow icon="mail-outline" label="Email" value={user?.email ?? '—'} />
          <View style={styles.separator} />
          <InfoRow icon="person-outline" label="Usuario" value={user?.username ?? '—'} />
        </View>

        {/* Sesión section */}
        <Text style={styles.sectionLabel}>Sesión</Text>
        <View style={styles.card}>
          <TouchableOpacity
            style={[styles.actionRow, isLoading && styles.rowDisabled]}
            onPress={handleLogout}
            disabled={isLoading}
            activeOpacity={0.75}
            accessibilityRole="button"
            accessibilityLabel="Cerrar sesión"
          >
            <View style={styles.rowLeft}>
              <Ionicons name="log-out-outline" size={ICON_SIZE} color={Colors.primary} />
              <Text style={styles.rowLabelDestructive}>Cerrar sesión</Text>
            </View>
            <Ionicons name="chevron-forward" size={16} color={Colors.primary} />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </Screen>
  );
}

interface InfoRowProps {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
}

function InfoRow({ icon, label, value }: InfoRowProps) {
  return (
    <View style={styles.infoRow}>
      <View style={styles.rowLeft}>
        <Ionicons name={icon} size={ICON_SIZE} color={Colors.textMuted} />
        <View style={styles.rowText}>
          <Text style={styles.rowLabel}>{label}</Text>
          <Text style={styles.rowValue}>{value}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1 },
  content: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.xxl,
  },

  header: {
    marginBottom: Spacing.xl,
    gap: Spacing.xs,
  },
  eyebrow: {
    fontSize: Typography.size.xs,
    fontWeight: Typography.weight.semibold,
    color: Colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  fullName: {
    fontSize: Typography.size.xxl,
    fontWeight: Typography.weight.bold,
    color: Colors.text,
  },
  username: {
    fontSize: Typography.size.md,
    color: Colors.textMuted,
  },

  sectionLabel: {
    fontSize: Typography.size.xs,
    fontWeight: Typography.weight.semibold,
    color: Colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: Spacing.sm,
    marginLeft: Spacing.xs,
  },

  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.lg,
    overflow: 'hidden',
    ...Shadow.sm,
  },

  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
  },
  rowDisabled: {
    opacity: 0.5,
  },
  rowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },
  rowText: {
    gap: 2,
  },
  rowLabel: {
    fontSize: Typography.size.xs,
    color: Colors.textMuted,
  },
  rowValue: {
    fontSize: Typography.size.md,
    color: Colors.text,
    fontWeight: Typography.weight.medium,
  },
  rowLabelDestructive: {
    fontSize: Typography.size.md,
    fontWeight: Typography.weight.medium,
    color: Colors.primary,
  },

  separator: {
    height: 1,
    backgroundColor: Colors.border,
    marginLeft: Spacing.md + ICON_SIZE + Spacing.md, // align with text, past icon
  },
});
