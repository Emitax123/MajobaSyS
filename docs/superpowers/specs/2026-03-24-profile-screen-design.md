# Profile Screen — Design Spec
**Date:** 2026-03-24
**Status:** Approved

---

## Overview

Replace the placeholder `src/app/(app)/profile.tsx` with a fully implemented profile screen. The screen is already registered in the tab bar as the 4th tab ("Perfil", icon `person-outline`) and requires no navigation changes.

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
User data is read directly from `useAuthStore((s) => s.user)` — no network call required. The store is populated on login and persists in memory for the session.

### Logout Flow
1. User taps "Cerrar sesión"
2. `Alert.alert` shows with "Cancelar" + "Cerrar sesión" (destructive) buttons
3. On confirm → `authStore.logout()` is called
4. `AppLayout` (`src/app/(app)/_layout.tsx`) already handles the redirect: when `!isAuthenticated` it renders `<Redirect href="/(auth)/login" />`

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
| Logout row | `TouchableOpacity` with destructive color |
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
- [ ] Tapping logout shows Alert with two buttons
- [ ] Canceling Alert dismisses without action
- [ ] Confirming logout clears session and redirects to login screen
