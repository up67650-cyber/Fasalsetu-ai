# FasalSetu AI — Project Progress

Last updated: 2026-11-19 — full-stack functionality update

## Status

The end-to-end implementation is present and smoke-tested. Weather location, farm/crop/activity records, advisory history, dashboard statistics and assistant configuration are persisted or served by the FastAPI/SQLite backend. Crop Doctor has an optional, genuine TensorFlow inference path and a documented PlantVillage transfer-learning workflow. No disease classifier weights are installed: it remains in explicit demo mode until a compatible artifact is trained, installed and evaluated.

## Completed

- [x] Phase 1 — Created the project structure, Vite/React setup, Tailwind configuration and professional dashboard.
- [x] Phase 2 — Added dashboard, Crop Doctor, Weather Intelligence, Crop Advisory, Farm Assistant and My Farm pages with responsive navigation.
- [x] Phase 3 — Added FastAPI service, API client, CORS configuration and health endpoint.
- [x] Phase 4 — Integrated Open-Meteo forecast and transparent forecast-based weather risk checks.
- [x] Added Open-Meteo location search to Weather Intelligence and connected selected coordinates to dashboard/weather data.
- [x] Completed functional audit in `FUNCTIONALITY_AUDIT.md`; tightened image validation, surfaced farm/history load errors, and refreshed activity after successful writes.
- [~] Phase 5 — Added backend image decoding/validation, safe optional MobileNetV2 model loading and inference, confidence warnings, curated non-prescriptive guidance, status reporting, and a PlantVillage transfer-learning/data-preparation path. No disease checkpoint was downloaded or trained; predictions remain unavailable until a compatible model is installed and field-evaluated.
- [x] Phase 6 — Added conservative rule-based crop advice and a curated English/Hindi fallback labeled as non-AI guidance.
- [x] Phase 7 — Added SQLite farm profile and history persistence.
- [x] Phase 7 — Added SQLite persistence for selected weather location, crop records and field activities; added database-backed dashboard summary and history chart.
- [x] Phase 6 — Added configurable backend-only OpenAI-compatible assistant integration, status reporting, contextual farm details, and explicitly labeled English/Hindi fallback responses.
- [~] Phase 8 — Expanded English/Hindi translations across navigation, weather, Crop Doctor (including diagnosis guidance when a model is present), advisory and farm forms. Some page copy and user-entered history details remain in their original language.
- [x] Phase 10 — Added setup, API, limitations and demo notes in `README.md`.
- [x] Researched public MobileNetV2 disease checkpoints and the PlantVillage dataset license; rejected candidate checkpoints with unclear provenance/class mappings or unclear license compatibility. Documented sources and decision in `README.md`.
- [x] Added focused Crop Doctor API tests covering unsupported/corrupt images, honest no-model behavior, and response formatting/uncertainty using a test-only model stub.

## Validation still required

- [x] Phase 9 — Frontend production build, backend API/SQLite checks and browser smoke tests completed.
- [x] Crop Doctor integration tests passed: `python -m unittest backend.test_crop_disease` (9 tests), including Hindi safety guidance.
- [x] TensorFlow architecture smoke check passed without downloads or saving a model: output shape `(None, 38)` and input rescaling maps `[0, 127.5, 255]` to `[-1, 0, 1]`.
- [x] Live Crop Doctor browser check passed: status API returned 200, demo-mode label displayed, Analyze disabled with a clear message, and no console errors.
- [x] Frontend build passed after Crop Doctor updates; existing Vite chunk-size advisory remains.
- [x] Verified live Open-Meteo access from the current environment.
- [x] Verified all feature pages render and mobile navigation opens in a browser.

## Important limitations / unfinished work

- Disease prediction remains unavailable in this checkout because no licensed/provenance-verified plant-disease weights were suitable. The TensorFlow inference path is ready for the generated `model.keras` + `metadata.json` artifact, but real-model inference and sample-image evaluation have not been performed.
- PlantVillage is identified by the authors' Hugging Face dataset page as CC BY-SA 3.0. Review attribution/share-alike obligations. The official Keras source is Apache-2.0, but that does not establish the terms of its separate ImageNet checkpoint/data; its download is opt-in in the training command and must be reviewed before use.
- The farm profile location is free text and is not automatically synchronized with the separately saved forecast location.
- Hindi translation covers major navigation, weather, Crop Doctor, advisory and farm-form copy, but does not translate every page label or stored history text.
- The generative assistant needs an externally configured provider and API key; without them it uses its explicitly labeled curated fallback.
- No authentication or multi-farmer tenancy is implemented; SQLite currently represents one local farm profile.
- Vite reports a 647.64 kB minified JavaScript chunk (183.69 kB gzip); production build succeeds, but code splitting is a future performance improvement.

## Key files

- Frontend: `src/App.jsx`, `src/api.js`, `src/styles.css`, `src/main.jsx`
- Backend: `backend/main.py`, `backend/crop_disease.py`, `backend/disease_guidance.py`, `backend/prepare_plantvillage.py`, `backend/train_disease_model.py`, `backend/test_crop_disease.py`
- Configuration: `package.json`, `vite.config.js`, `tailwind.config.js`, `requirements.txt`, `requirements-ml.txt`, `.env.example`
- Setup and continuity: `README.md`, `PROJECT_PROGRESS.md`

## Resume next

1. Read this file and inspect the existing files before editing.
2. Run `npm install`, `npm run build`, install `requirements.txt`, and run backend endpoint checks when making changes.
3. Before any model download, review the Keras ImageNet checkpoint/data terms and PlantVillage CC BY-SA 3.0 obligations. Prepare the dataset and run the documented training workflow only after accepting those terms.
4. Evaluate the generated checkpoint with representative, independently labeled Indian field images and local agricultural experts before enabling farm use. Do not describe PlantVillage test scores as field accuracy.

## Validation results (2026-11-19)

- `npm install` completed with 0 reported vulnerabilities.
- `npm run build` succeeded; output was 647.64 kB minified / 183.69 kB gzip with the existing chunk-size advisory.
- `python -m compileall -q backend` passed; `python -m unittest backend.test_application backend.test_crop_disease` passed (21 tests).
- Browser smoke check verified navigation, persisted weather-location selection, live Open-Meteo conditions, Hindi weather rendering, Crop Doctor preview/invalid-file handling and translated error, advisory/assistant flows, and farm record forms. Open-Meteo intermittently timed out; the API returned an explicit 503 instead of fabricated data.
- Functional audit details, verified scenarios and remaining limitations are in `FUNCTIONALITY_AUDIT.md`.
- Crop diagnosis API tests verify content-type, file-size and decode handling, explicit 503 behavior without model weights, and response/guidance/uncertainty formatting with a non-persistent test double. No disease model sample-image evaluation has been claimed.
- TensorFlow/Keras runtime check verified the training graph has 38 outputs and the embedded MobileNetV2 preprocessing maps 0–255 pixels to -1–1; it used random initialization only, saved no artifact, and is not a disease-classifier evaluation.
