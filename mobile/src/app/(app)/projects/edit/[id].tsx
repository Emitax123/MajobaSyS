import { useState, useEffect } from 'react';
import {
  View, Text, TextInput, StyleSheet, TouchableOpacity,
  ScrollView, ActivityIndicator, Platform, Modal, Switch, Alert,
  KeyboardAvoidingView,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { projectsService } from '@/services/projects.service';
import { Colors, Typography, Spacing, Radius, Shadow } from '@/constants/theme';
import Screen from '@/components/layout/Screen';

type DateField = 'start_date' | 'end_date';

export default function EditProjectScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const [fetching, setFetching] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [clientName, setClientName] = useState<string | null>(null);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState<Date>(new Date());
  const [hasEndDate, setHasEndDate] = useState(false);
  const [isActive, setIsActive] = useState(true);

  const [activeDateField, setActiveDateField] = useState<DateField | null>(null);
  const [tempDate, setTempDate] = useState(new Date());

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const toISODate = (date: Date) => date.toISOString().split('T')[0];
  const toDisplayDate = (date: Date) =>
    date.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });

  useEffect(() => {
    const projectId = Number(id);
    if (!projectId) {
      setFetchError('ID de proyecto inválido.');
      setFetching(false);
      return;
    }
    setFetching(true);
    projectsService.get(projectId)
      .then((data) => {
        setClientName(data.client_name ?? null);
        setName(data.name);
        setDescription(data.description ?? '');
        setLocation(data.location ?? '');
        setStartDate(data.start_date ? new Date(data.start_date) : new Date());
        setHasEndDate(!!data.end_date);
        setEndDate(data.end_date ? new Date(data.end_date) : new Date());
        setIsActive(data.is_active);
      })
      .catch(() => setFetchError('No se pudo cargar el proyecto.'))
      .finally(() => setFetching(false));
  }, [id]);

  const openDatePicker = (field: DateField) => {
    setTempDate(field === 'start_date' ? startDate : endDate);
    setActiveDateField(field);
  };

  const confirmDate = () => {
    if (activeDateField === 'start_date') setStartDate(tempDate);
    else setEndDate(tempDate);
    setActiveDateField(null);
  };

  const handleAndroidDateChange = (event: DateTimePickerEvent, date?: Date) => {
    setActiveDateField(null);
    if (event.type === 'set' && date) {
      if (activeDateField === 'start_date') setStartDate(date);
      else setEndDate(date);
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!name.trim()) newErrors.name = 'El nombre es obligatorio.';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await projectsService.update(Number(id), {
        name: name.trim(),
        description: description.trim() || undefined,
        location: location.trim() || undefined,
        start_date: toISODate(startDate),
        end_date: hasEndDate ? toISODate(endDate) : null,
        is_active: isActive,
      });
      router.back();
    } catch (e: unknown) {
      const data = (e as { response?: { data?: { name?: string[]; detail?: string } } })?.response?.data;
      const detail = data?.name?.[0] ?? data?.detail ?? 'No se pudo guardar el proyecto.';
      Alert.alert('Error', detail);
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <Screen>
        <View style={styles.center}>
          <ActivityIndicator color={Colors.primary} size="large" />
        </View>
      </Screen>
    );
  }

  if (fetchError) {
    return (
      <Screen>
        <View style={styles.center}>
          <Text style={styles.errorText}>{fetchError}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={() => router.back()}>
            <Text style={styles.retryText}>Volver</Text>
          </TouchableOpacity>
        </View>
      </Screen>
    );
  }

  return (
    <Screen>
      <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.header}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backBtn} activeOpacity={0.7}>
              <Text style={styles.backText}>← Volver</Text>
            </TouchableOpacity>
            <Text style={styles.title}>Editar Proyecto</Text>
            {clientName ? (
              <View style={styles.clientBadge}>
                <Text style={styles.clientBadgeText}>{clientName}</Text>
              </View>
            ) : null}
          </View>

          <View style={styles.form}>
            <View style={styles.field}>
              <Text style={styles.label}>Nombre <Text style={styles.required}>*</Text></Text>
              <TextInput
                style={[styles.input, errors.name ? styles.inputError : null]}
                value={name}
                onChangeText={(v) => { setName(v); setErrors((p) => ({ ...p, name: '' })); }}
                placeholder="Nombre del proyecto"
                placeholderTextColor={Colors.textDisabled}
                autoCapitalize="words"
                returnKeyType="next"
              />
              {errors.name ? <Text style={styles.errorText}>{errors.name}</Text> : null}
            </View>

            <View style={styles.field}>
              <Text style={styles.label}>Descripción</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={description}
                onChangeText={setDescription}
                placeholder="Descripción del proyecto (opcional)"
                placeholderTextColor={Colors.textDisabled}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.field}>
              <Text style={styles.label}>Ubicación</Text>
              <TextInput
                style={styles.input}
                value={location}
                onChangeText={setLocation}
                placeholder="Dirección o lugar del proyecto (opcional)"
                placeholderTextColor={Colors.textDisabled}
                autoCapitalize="words"
                returnKeyType="done"
              />
            </View>

            <View style={styles.field}>
              <Text style={styles.label}>Fecha de inicio <Text style={styles.required}>*</Text></Text>
              <TouchableOpacity
                style={styles.dateBtn}
                onPress={() => openDatePicker('start_date')}
                activeOpacity={0.8}
                accessibilityRole="button"
                accessibilityLabel="Seleccionar fecha de inicio"
              >
                <Text style={styles.dateBtnText}>{toDisplayDate(startDate)}</Text>
                <Text style={styles.dateBtnIcon}>📅</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.field}>
              <View style={styles.switchRow}>
                <Text style={styles.label}>Fecha de fin</Text>
                <Switch
                  value={hasEndDate}
                  onValueChange={setHasEndDate}
                  trackColor={{ false: Colors.bgElevated, true: Colors.primaryLight }}
                  thumbColor={hasEndDate ? Colors.primary : Colors.textMuted}
                />
              </View>
              {hasEndDate ? (
                <TouchableOpacity
                  style={[styles.dateBtn, styles.dateBtnMt]}
                  onPress={() => openDatePicker('end_date')}
                  activeOpacity={0.8}
                  accessibilityRole="button"
                  accessibilityLabel="Seleccionar fecha de fin"
                >
                  <Text style={styles.dateBtnText}>{toDisplayDate(endDate)}</Text>
                  <Text style={styles.dateBtnIcon}>📅</Text>
                </TouchableOpacity>
              ) : null}
            </View>

            <View style={styles.field}>
              <View style={styles.switchRow}>
                <Text style={styles.label}>Estado activo</Text>
                <Switch
                  value={isActive}
                  onValueChange={setIsActive}
                  trackColor={{ false: Colors.bgElevated, true: Colors.primaryLight }}
                  thumbColor={isActive ? Colors.primary : Colors.textMuted}
                />
              </View>
              <Text style={styles.switchHint}>
                {isActive ? 'El proyecto está activo' : 'El proyecto está inactivo'}
              </Text>
            </View>
          </View>

          <TouchableOpacity
            style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
            onPress={handleSubmit}
            disabled={loading}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel="Guardar cambios"
          >
            {loading
              ? <ActivityIndicator color={Colors.white} />
              : <Text style={styles.submitText}>Guardar cambios</Text>}
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>

      {Platform.OS === 'ios' && activeDateField !== null && (
        <Modal transparent animationType="slide">
          <View style={styles.modalOverlay}>
            <View style={styles.modalCard}>
              <Text style={styles.modalTitle}>
                {activeDateField === 'start_date' ? 'Fecha de inicio' : 'Fecha de fin'}
              </Text>
              <DateTimePicker
                value={tempDate}
                mode="date"
                display="spinner"
                onChange={(_, date) => { if (date) setTempDate(date); }}
                locale="es"
                style={styles.iosPicker}
              />
              <View style={styles.modalBtns}>
                <TouchableOpacity style={styles.modalBtnCancel} onPress={() => setActiveDateField(null)} activeOpacity={0.8}>
                  <Text style={styles.modalBtnCancelText}>Cancelar</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.modalBtnConfirm} onPress={confirmDate} activeOpacity={0.8}>
                  <Text style={styles.modalBtnConfirmText}>Confirmar</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
      )}

      {Platform.OS === 'android' && activeDateField !== null && (
        <DateTimePicker
          value={tempDate}
          mode="date"
          display="default"
          onChange={handleAndroidDateChange}
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  scroll: { flex: 1 },
  content: { padding: Spacing.lg, gap: Spacing.md, paddingBottom: Spacing.xxl },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: Spacing.md },
  header: { gap: Spacing.xs, marginBottom: Spacing.sm },
  backBtn: { alignSelf: 'flex-start' },
  backText: { fontSize: Typography.size.sm, color: Colors.primary, fontWeight: Typography.weight.medium },
  title: { fontSize: Typography.size.xxl, fontWeight: Typography.weight.bold, color: Colors.text },
  clientBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: Radius.pill,
    backgroundColor: Colors.primaryLight,
  },
  clientBadgeText: { fontSize: Typography.size.xs, color: Colors.primary, fontWeight: Typography.weight.medium },
  form: {
    backgroundColor: Colors.bgCard,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: Spacing.md,
    ...Shadow.sm,
  },
  field: { gap: Spacing.xs },
  label: { fontSize: Typography.size.sm, fontWeight: Typography.weight.medium, color: Colors.textMuted },
  required: { color: Colors.primary },
  input: {
    backgroundColor: Colors.bgElevated,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    fontSize: Typography.size.md,
    color: Colors.text,
  },
  inputError: { borderColor: Colors.error },
  textArea: { minHeight: 80, paddingTop: Spacing.sm },
  errorText: { fontSize: Typography.size.xs, color: Colors.error },
  dateBtn: {
    backgroundColor: Colors.bgElevated,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dateBtnMt: { marginTop: Spacing.xs },
  dateBtnText: { fontSize: Typography.size.md, color: Colors.text },
  dateBtnIcon: { fontSize: Typography.size.md },
  switchRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  switchHint: { fontSize: Typography.size.xs, color: Colors.textDisabled },
  submitBtn: {
    backgroundColor: Colors.primary,
    borderRadius: Radius.md,
    paddingVertical: Spacing.md,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  submitBtnDisabled: { opacity: 0.6 },
  submitText: { fontSize: Typography.size.md, fontWeight: Typography.weight.semibold, color: Colors.white },
  modalOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: Colors.overlay },
  modalCard: {
    backgroundColor: Colors.bgCard,
    borderTopLeftRadius: Radius.xl,
    borderTopRightRadius: Radius.xl,
    paddingTop: Spacing.lg,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xl,
    borderTopWidth: 1,
    borderColor: Colors.border,
  },
  modalTitle: {
    fontSize: Typography.size.lg,
    fontWeight: Typography.weight.semibold,
    color: Colors.text,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  iosPicker: { backgroundColor: Colors.bgCard },
  modalBtns: { flexDirection: 'row', gap: Spacing.sm, marginTop: Spacing.md },
  modalBtnCancel: {
    flex: 1, paddingVertical: Spacing.md, borderRadius: Radius.md,
    backgroundColor: Colors.bgElevated, borderWidth: 1, borderColor: Colors.border, alignItems: 'center',
  },
  modalBtnCancelText: { fontSize: Typography.size.md, color: Colors.text, fontWeight: Typography.weight.medium },
  modalBtnConfirm: {
    flex: 1, paddingVertical: Spacing.md, borderRadius: Radius.md,
    backgroundColor: Colors.primary, alignItems: 'center',
  },
  modalBtnConfirmText: { fontSize: Typography.size.md, color: Colors.white, fontWeight: Typography.weight.semibold },
  retryBtn: {
    paddingHorizontal: Spacing.lg, paddingVertical: Spacing.sm, borderRadius: Radius.md,
    backgroundColor: Colors.bgElevated, borderWidth: 1, borderColor: Colors.border,
  },
  retryText: { fontSize: Typography.size.sm, color: Colors.text },
});
