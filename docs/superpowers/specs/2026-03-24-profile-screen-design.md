# Profile Screen — Design Spec
**Date:** 2026-03-24
**Status:** Approved

---

## Overview

Replace the placeholder `src/app/(app)/profile.tsx` with a fully implemented profile screen. The screen is already registered in the tab bar as the 4th `<Tabs.Screen>` entry (3rd visible tab: Inicio → Clientes → Perfil) and requires no navigation changes.

---

## Scope

**In scope:**
- Display authenticated user's data: full name, username, email
- Logout button with confirmation alert

**Out of scope:**
- Avatar / profile image
- Manager/gamification data (level, points, progress)
- Account settings (change password, preferences)

---

## Architecture

### Data Source
User data is read from `useAuthStore((s) => s.user)` — no network call required. The store is populated on login and held in memory for the duration of the session.

**Known limitation — cold-start hydration:** `hydrateFromStorage` restores `isAuthenticated: true` from SecureStore when `rememberMe` is enabled, but it does **not** restore the `user` object (user data is not serialized to SecureStore). This means on a cold app start the profile screen can mount with `user === null` while `isAuthenticated === true`. The screen must handle this gracefully.

**Null guard requirement:** All user fields (`full_name`, `username`, `email`) must be read with a safe fallback (`user?.full_name ?? '—'`). If `user` is null, the screen renders the layout with empty/dash placeholders — no crash.

### Logout Flow
1. User taps "Cerrar sesión"
2. `Alert.alert` shows with "Cancelar" + "Cerrar sesión" (destructive) buttons
3. On confirm → `authStore.logout()` is called
4. While logout is in progress (`isLoading: true`), the logout row must be disabled (no double-tap)
5. `AppLayout` (`src/app/(app)/_layout.tsx`) handles the redirect automatically: when `!isAuthenticated` it renders `<Redirect href="/(auth)/login" />`

---

## Layout

Settings-list pattern (iOS/Android native convention):

```
PERFIL                          ← eyebrow (red, uppercase, letterSpacing)
Emanuel Jiménez                 ← full_name (xxl bold, Colors.text)
@emitax123                      ← username (md, Colors.textMuted)

CUENTA                          ← section label
┌──────────────────────────────┐
│ [icon] Email                  │ ← row with label + value
│        emitax@example.com     │
├──────────────────────────────┤
│ [icon] Usuario                │ ← row with label + value
│        emitax123              │
└──────────────────────────────┘

SESIÓN                          ← section label
┌──────────────────────────────┐
│ [icon] Cerrar sesión          │ ← destructive row (Colors.primary / red)
│                               │   disabled + opacity 0.5 while isLoading
└──────────────────────────────┘
```

---

## Components

All implemented inline in `profile.tsx` — no new shared components needed.

| Element | Implementation |
|---|---|
| `Screen` | Existing `@/components/layout/Screen` wrapper |
| Section label | `eyebrow` text pattern from dashboard |
| Info row | `View` with icon (`Ionicons`), label, value |
| Logout row | `TouchableOpacity` with destructive color, `disabled` when `isLoading` |
| Confirmation | `Alert.alert` (React Native built-in) |

---

## Design Tokens

Uses existing tokens from `@/constants/theme` — no new dependencies:

- `Colors.bgCard` — row background
- `Colors.border` — row separators and card border
- `Colors.primary` — eyebrow label, logout row icon + text
- `Colors.text` / `Colors.textMuted` — content hierarchy
- `Typography.size.*`, `Typography.weight.*`
- `Spacing.*`, `Radius.*`, `Shadow.sm`

---

## Files Affected

| File | Change |
|---|---|
| `mobile/src/app/(app)/profile.tsx` | Full replacement of placeholder |

No other files need modification.

---

## Testing

Manual verification:
- [ ] Profile tab renders without error when authenticated
- [ ] `full_name`, `username`, `email` display correctly from store
- [ ] Screen renders with fallback dashes (`—`) when `user` is null (cold-start hydration scenario)
- [ ] Tapping logout shows Alert with two buttons
- [ ] Canceling Alert dismisses without action
- [ ] Confirming logout clears session and redirects to login screen
- [ ] Logout row is disabled (no second tap) while logout is in progress
