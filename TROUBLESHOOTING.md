# Troubleshooting Blank Page Issue

## Quick Checks

1. **Open Browser Developer Tools** (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab to see if CSS/JS files are loading
   - Look for 404 errors on `/static/css/style.css` or `/static/js/auth.js`

2. **Try Direct Access:**
   - Direct: `http://192.168.1.137:8000`
   - Via Caddy: `http://your-domain.com:8080`

3. **Clear Browser Cache:**
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
   - Or clear cache and reload

4. **Check if CSS is Loading:**
   ```bash
   curl -H "Host: your-domain.com" http://localhost:8080/static/css/style.css | head -5
   ```

## Common Issues

### Issue 1: CSS Not Loading
**Symptom:** Page loads but appears blank/white
**Solution:** Check browser console for 404 errors on CSS files

### Issue 2: JavaScript Error
**Symptom:** Page loads but nothing happens
**Solution:** Check browser console for JavaScript errors

### Issue 3: Redirect Loop
**Symptom:** Page keeps redirecting
**Solution:** Clear localStorage: `localStorage.clear()` in browser console

### Issue 4: CORS Issues
**Symptom:** Network errors in console
**Solution:** Check Caddy configuration for proper headers

## Test Commands

```bash
# Test main page
curl -H "Host: tickets.gmojsoski.com" http://localhost:8080/

# Test login page
curl -H "Host: your-domain.com" http://localhost:8080/login

# Test CSS
curl -H "Host: your-domain.com" http://localhost:8080/static/css/style.css

# Test JS
curl -H "Host: your-domain.com" http://localhost:8080/static/js/auth.js

# Test API
curl -H "Host: your-domain.com" http://localhost:8080/api/health
```

## Expected Behavior

1. **First Visit (Not Logged In):**
   - Should redirect to `/login`
   - Should show login form

2. **After Login:**
   - Should redirect to `/`
   - Should show upload interface

3. **If Already Logged In:**
   - Should show main page directly

