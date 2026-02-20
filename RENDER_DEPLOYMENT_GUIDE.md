# 🚀 DEPLOY TO RENDER - COMPLETE GUIDE

Since you already pay for Render, let's use it!

---

## 📋 STEP-BY-STEP DEPLOYMENT

### STEP 1: Prepare Your Files

Make sure you have these files in your project folder:

**Required Files:**
1. ✅ `integrated_backend.py` (updated for Render)
2. ✅ `final_competitor_profiler_complete.py` (your profiler)
3. ✅ `requirements.txt` (Python packages)
4. ✅ `render.yaml` (Render configuration)
5. ✅ `.env` (your API keys - DON'T upload this!)

---

### STEP 2: Create GitHub Repository

**Option A: Via GitHub Website**

1. Go to https://github.com
2. Click "New repository"
3. Name: `space-intel-backend`
4. Make it **Private** (important!)
5. Click "Create repository"

6. Upload your files:
   - `integrated_backend.py`
   - `final_competitor_profiler_complete.py`
   - `requirements.txt`
   - `render.yaml`
   - **DON'T upload .env!**

**Option B: Via Command Line**

```powershell
# Initialize git
git init

# Add files
git add integrated_backend.py
git add final_competitor_profiler_complete.py
git add requirements.txt
git add render.yaml

# DON'T add .env - it has your API keys!
# Create .gitignore
echo ".env" > .gitignore
git add .gitignore

# Commit
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/space-intel-backend.git
git branch -M main
git push -u origin main
```

---

### STEP 3: Deploy to Render

1. **Login to Render**
   - Go to https://dashboard.render.com
   - Login with your account

2. **Create New Web Service**
   - Click "New +"
   - Select "Web Service"

3. **Connect GitHub**
   - Click "Connect GitHub"
   - Select your `space-intel-backend` repository
   - Click "Connect"

4. **Configure Service**
   
   **Name:** `space-intel-backend`
   
   **Region:** Oregon (US West) - or closest to you
   
   **Branch:** `main`
   
   **Build Command:**
   ```
   pip install -r requirements.txt
   ```
   
   **Start Command:**
   ```
   python integrated_backend.py
   ```
   
   **Plan:** Starter ($7/month) - you're already paying!

5. **Add Environment Variables**
   
   Click "Advanced" → "Add Environment Variable"
   
   Add ALL your API keys from `.env`:
   
   ```
   GOOGLE_CSE_API_KEY = your_key_here
   GOOGLE_CSE_ID = your_id_here
   GOOGLE_PLACES_API_KEY = your_key_here
   HUNTER_API_KEY = your_key_here
   DEEPSEEK_API_KEY = your_key_here
   LLM_ENABLED = true
   OPENPAGERANK_API_KEY = your_key_here
   BRAVE_SEARCH_API_KEY = your_key_here
   SERPAPI_KEY = your_key_here
   SCRAPERAPI_KEY = your_key_here
   RAPIDAPI_KEY = your_key_here
   ```
   
   **IMPORTANT:** Copy these from your `.env` file!

6. **Create Service**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment

---

### STEP 4: Get Your URL

After deployment completes, you'll get a URL like:

```
https://space-intel-backend.onrender.com
```

**Test it:**
```
https://space-intel-backend.onrender.com/api/auth/login
```

Should show: "Method not allowed" (means it's working!)

---

### STEP 5: Update Your Dashboard

Download your `COMPLETE_SYSTEM.html` and update ALL fetch URLs:

**Find and Replace:**

```javascript
// CHANGE THIS:
fetch('http://localhost:5000/api/auth/login', ...)

// TO THIS:
fetch('https://YOUR-APP-NAME.onrender.com/api/auth/login', ...)
```

**4 places to update:**
1. Login: `/api/auth/login`
2. Logout: `/api/auth/logout`
3. Run Analysis: `/api/run-analysis`
4. Export: `/api/export/csv` and `/api/export/excel`

**Example:**
```javascript
// Login function
async function login() {
    const response = await fetch('https://space-intel-backend.onrender.com/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({email, password})
    });
    // ... rest of code
}
```

---

### STEP 6: Host Your Dashboard

**Option A: Render Static Site (Easiest!)**

1. In Render Dashboard, click "New +"
2. Select "Static Site"
3. Upload `COMPLETE_SYSTEM.html`
4. Deploy!
5. Get URL: `https://your-dashboard.onrender.com`

**Option B: Vercel (Alternative)**

1. Go to https://vercel.com
2. Sign up
3. Click "New Project"
4. Upload `COMPLETE_SYSTEM.html`
5. Deploy!
6. Get URL: `https://your-dashboard.vercel.app`

---

## ✅ FINAL RESULT

### Your System URLs:

**Backend API:**
```
https://space-intel-backend.onrender.com
```

**Dashboard:**
```
https://your-dashboard.onrender.com
```

### Users Access:

1. Go to: `https://your-dashboard.onrender.com`
2. Login: `demo@customer.com` / `demo123`
3. Enter: Industry + Location
4. Click: "🚀 ANALYZE"
5. Wait: 3-5 minutes
6. See: Charts, stats, data table!
7. Export: CSV or Excel

**NO commands needed!** 🎉

---

## 🔧 TROUBLESHOOTING

### Issue: "Application failed to respond"

**Fix:**
```
Check Render logs:
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. Look for errors
```

### Issue: "Module not found"

**Fix:**
```
Add missing package to requirements.txt:
1. Edit requirements.txt
2. Add the missing package
3. Git commit and push
4. Render auto-redeploys
```

### Issue: "CORS error"

**Fix:**
```
Already handled in integrated_backend.py!
CORS(app, supports_credentials=True)
```

---

## 💰 COST BREAKDOWN

You're already paying for Render:

**What you have:**
- Starter Plan: $7/month

**What this uses:**
- 1 Web Service: Included in your plan!
- 1 Static Site: FREE

**Total extra cost: $0**

You're just using what you already pay for! 🎉

---

## 🚀 QUICK DEPLOY CHECKLIST

- [ ] Files on GitHub (without .env)
- [ ] Render web service created
- [ ] Environment variables added
- [ ] Service deployed successfully
- [ ] Got backend URL
- [ ] Updated dashboard with backend URL
- [ ] Dashboard deployed
- [ ] Tested login
- [ ] Tested analysis
- [ ] Working! ✅

---

## 📝 MAINTENANCE

**To Update Your Code:**

```powershell
# Make changes to your files
# Then:
git add .
git commit -m "Updated feature"
git push

# Render auto-deploys in 2-5 minutes!
```

---

## 🎯 NEXT STEPS

1. Deploy backend to Render (15 min)
2. Update dashboard URLs (5 min)
3. Deploy dashboard (5 min)
4. Test everything (5 min)

**Total time: 30 minutes**

Ready to deploy? Let me know if you need help with any step!
