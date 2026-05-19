## Render deployment tasks
- [x] Confirm deployment approach (two services).

- [ ] Add `render.yaml` with backend + frontend services.
- [ ] Add `RENDER_DEPLOYMENT.md` documenting required Render env vars.
- [ ] Add frontend production setup for serving Vite `dist/`.
- [ ] Ensure frontend API base uses `VITE_API_BASE_URL` (and no dev-proxy dependency).
- [ ] Ensure backend works on Render (migrations/bootstrapping strategy, gunicorn command, allowed hosts).
- [ ] Add lightweight static handling for frontend and ensure CORS/origin settings.
- [ ] Run local build checks (frontend build, Django collect/migrate commands if applicable).
- [ ] Final verification checklist for Render.

