# Baseline Research Registry: Deployment Guide

## Overview
The Registry frontend is a Vite+React static site ready to deploy to Vercel, Netlify, or any static host. All dependencies are installed, the build is tested and passing.

## Pre-Deployment Checklist
- [ ] **Brand name finalized** (Baseline, Corpus, Cleartext, etc.)
- [ ] **Domain purchased** and ready to point
- [ ] **GitHub repo is public** (or will be made public)

## Deployment Option 1: Vercel (Recommended)

### Step 1: Create Vercel Account & Connect Repository
1. Go to [vercel.com](https://vercel.com)
2. Sign up or log in
3. Click "New Project" → "Import Git Repository"
4. Select `humans-benefiting-from-ai/baseline-research` (GitHub or GitLab)

### Step 2: Configure Build Settings
Vercel auto-detects the setup. Verify:
- **Framework:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Root Directory:** `registry/web`

### Step 3: Add Environment Variables (Optional)
No required environment variables. If you want to track deployments:
- `REACT_APP_VERSION`: Set to commit SHA or version tag

### Step 4: Deploy
Click "Deploy." Vercel will:
1. Clone the repo
2. Install dependencies
3. Run build
4. Deploy to `baseline-research.vercel.app` (temporary URL)

### Step 5: Connect Custom Domain
1. In Vercel dashboard, go to **Settings → Domains**
2. Click "Add Domain"
3. Enter your domain (e.g., `baseline-research.io`)
4. Vercel provides DNS records to add to your registrar
5. DNS propagation typically takes 5-30 minutes

### Step 6: HTTPS & SSL
Vercel auto-provisions free SSL. After DNS is confirmed, you'll get an HTTPS certificate automatically.

---

## Deployment Option 2: Netlify

### Step 1: Connect Repository
1. Go to [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Authorize GitHub and select the repo

### Step 2: Build Settings
- **Base directory:** `registry/web`
- **Build command:** `npm run build`
- **Publish directory:** `dist`

### Step 3: Deploy & Domain
Deploy automatically runs. Then:
1. Go to **Domain settings**
2. Click "Add custom domain"
3. Point your domain's DNS to Netlify

---

## Deployment Option 3: GitHub Pages (Free, But Limited)

If you prefer GitHub Pages, you can:
```bash
# In registry/web directory
npm run build
git add dist/
git commit -m "chore: Deploy to GitHub Pages"
git push
```

Then enable GitHub Pages in repo settings to serve from `gh-pages` branch.

---

## After Deployment

### Analytics & Monitoring (Optional)
- Add Google Analytics to `registry/web/index.html`
- Add Sentry error tracking for production issues

### DNS Setup Checklist
- [ ] DNS records propagated
- [ ] HTTPS working (green lock in browser)
- [ ] Registry loads at `https://yourdomain.com`
- [ ] Whitepaper accessible at `https://yourdomain.com/whitepaper`

### Social & Announcement
Once live:
1. Update `registry/web/src/App.tsx` line 42 branding if using a different domain name
2. Rebuild and redeploy
3. Share registry URL on LinkedIn, Twitter, WhatsApp

---

## Troubleshooting

**Build fails on deploy:**
- Check that `npm run build` passes locally
- Verify all dependencies are listed in `package.json`
- Run `npm ci` (clean install) locally to debug

**Domain doesn't resolve:**
- Wait 5-30 minutes for DNS propagation
- Check DNS records in your registrar (should match Vercel/Netlify instructions)
- Use [DNS Checker](https://dnschecker.org) to verify globally

**HTTPS not working:**
- Force HTTPS in Vercel/Netlify settings
- Clear browser cache (Cmd+Shift+Delete or Ctrl+Shift+Delete)

---

## Future Updates

The Registry is set up for automatic CI/CD:
- **GitHub Actions** (optional): On push to `main`, rebuild and deploy
- **Vercel auto-deploy**: Every push to main auto-redeploys

To update the Registry:
1. Edit `registry/web/src/data/registry.json` (add new tools)
2. Commit and push to `main`
3. Vercel/Netlify auto-redeploys (~2-5 min)

---

## Questions?
Review the latest Vite docs at [vitejs.dev](https://vitejs.dev) or Vercel docs at [vercel.com/docs](https://vercel.com/docs).
