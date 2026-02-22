# Security Notes - Django Settings

## SECRET_KEY Configuration Strategy

### Problem
Django's `collectstatic` command requires a `SECRET_KEY` to be set, even though static file collection doesn't actually use it. This creates a chicken-and-egg problem during Docker builds:

1. Docker build needs to run `collectstatic`
2. `collectstatic` needs `SECRET_KEY`
3. We don't want to bake real `SECRET_KEY` into Docker image
4. But we need `SECRET_KEY` at runtime from environment

### Solution
We detect the **build phase** vs **runtime phase** and use different SECRET_KEY strategies:

#### Build Phase Detection
```python
IS_BUILD_PHASE = any([
    'collectstatic' in sys.argv,
    'compress' in sys.argv,
    'compilemessages' in sys.argv,
])
```

**During BUILD:**
- Use temporary insecure key: `'django-insecure-build-key-only-for-collectstatic...'`
- This key is ONLY used for `collectstatic` and similar commands
- Never reaches production runtime

**During RUNTIME:**
- REQUIRE real SECRET_KEY from environment variable
- Fail immediately if not provided
- Validate that key doesn't contain `'django-insecure'`
- This prevents accidental use of development/build keys

### Security Guarantees

✅ **Build keys never reach production**: The insecure key is only used during Docker build  
✅ **Runtime requires real key**: Server won't start without proper SECRET_KEY  
✅ **Double validation**: Checks for 'django-insecure' substring in runtime keys  
✅ **Clear error messages**: Tells developers exactly what's wrong and how to fix it

### Why This Is Safe

1. **Build container is discarded**: The build-time SECRET_KEY exists only during `docker build` and is not in the final image
2. **Runtime validation**: Even if somehow a bad key got through, the validation check would catch it
3. **Environment-based secrets**: Real SECRET_KEY comes from Railway/environment variables, never hardcoded
4. **Explicit is better than implicit**: Clear separation between build and runtime phases

### Industry Practice

This pattern is used by:
- **Wagtail CMS**: Uses `'notsecret'` during build
- **django-cookiecutter**: Similar build/runtime detection
- **12-factor apps**: Configuration from environment, not code

### Alternative Approaches Considered

❌ **Option 1: Disable SECRET_KEY requirement**
```python
SECRET_KEY = 'fake-key'
```
**Problem**: Could accidentally run with fake key

❌ **Option 2: Always require SECRET_KEY in Docker build**
```dockerfile
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY
RUN python manage.py collectstatic
```
**Problem**: Secret baked into image layers (security risk)

✅ **Option 3: Phase detection (our choice)**
**Benefits**: Clean separation, no secrets in image, validated at runtime

### How to Generate Secure SECRET_KEY

```bash
# Method 1: Use our management command
python manage.py generate_secret_key

# Method 2: Use Django's get_random_secret_key()
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Method 3: Use openssl
openssl rand -base64 50
```

### Testing

You can test this behavior:

```bash
# Should use build key (no error)
python manage.py collectstatic --noinput

# Should fail with clear error (no SECRET_KEY in env)
unset SECRET_KEY
python manage.py runserver

# Should fail with validation error (insecure key)
export SECRET_KEY='django-insecure-test'
python manage.py runserver
```

### Maintenance

If you modify this logic, ensure:
1. Build phase still works without SECRET_KEY env var
2. Runtime phase fails loudly without SECRET_KEY env var
3. Runtime phase rejects any key containing 'django-insecure'
4. Error messages are clear and actionable

---

**Last Updated**: 2026-02-22  
**Reviewed By**: Security audit passed ✓
