# FasalSetu AI

A responsive agriculture assistant for farm weather, crop guidance and farm records. The project is designed to run locally without paid API keys.

## What works today

- React + Vite dashboard with responsive navigation and English/Hindi page copy.
- Live current conditions and 7-day weather via Open-Meteo (no API key required), forecast-based risk flags and irrigation checks.
- FastAPI backend with additive SQLite migrations, a saved weather location, farm crop records, field activity, advisories and history.
- Dashboard statistics and its 7-day activity chart are derived from SQLite history; soil sensor measurements are not simulated.
- Forecast-aware, rule-based crop guidance considers crop, soil, location, farm area and growth stage without inventing fertilizer or pesticide rates.
- Farm assistant can call a configurable OpenAI-compatible chat-completions API from the backend. Without a key or when the provider fails, it clearly labels curated English/Hindi fallback answers.
- Crop photo selection and preview, server-side image decoding, optional MobileNetV2 inference, and safe English/Hindi result guidance. This checkout has no disease checkpoint, so it displays demo mode and does not invent a prediction.

## Run locally

Prerequisites: Node.js 18+ and Python 3.10+.

1. Install frontend dependencies: `npm install`
2. Start the API in a terminal:
   - `python -m venv .venv`
   - Windows: `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `uvicorn backend.main:app --reload`
3. Start the web app in another terminal: `npm run dev`
4. Open the Vite URL (normally `http://localhost:5173`).

The API defaults to `http://localhost:8000`. Set `VITE_API_URL` in a root `.env` file to change it. Set `DATABASE_PATH` in the backend process environment to choose a different SQLite file. The default database is `backend/fasalsetu.db`. Startup applies additive schema migrations and preserves existing farm-profile and history rows.

### Optional generative assistant

The assistant uses curated rule-based responses unless an AI provider is configured. It supports OpenAI-compatible `POST /chat/completions` providers. Configure the following as environment variables for the **backend process** (not `VITE_` variables):

```powershell
$env:FARM_ASSISTANT_PROVIDER = "OpenAI-compatible"
$env:FARM_ASSISTANT_BASE_URL = "https://api.openai.com/v1"
$env:FARM_ASSISTANT_MODEL = "gpt-4o-mini"
$env:FARM_ASSISTANT_API_KEY = "your-provider-key"
uvicorn backend.main:app --reload
```

`.env.example` documents the variables but FastAPI does not automatically load it; set backend variables in the process manager or shell. Never put the provider key in frontend code or expose it through a `VITE_` variable. The assistant sends the question and limited farm context (crop, soil, growth stage and farm area) to the configured provider. Responses are labeled as AI-generated and should be checked locally. If configuration is absent or the provider is unavailable, the endpoint responds using an explicitly labeled curated fallback.

## Crop disease model

The backend has a real, optional TensorFlow/Keras inference path. It accepts JPEG, PNG, and WebP images up to 10 MB, verifies the encoded image, limits decoded dimensions, converts to RGB, resizes to 224×224, and loads the trained model and exact 38-class label map from `model.keras` and `metadata.json`. The model must perform MobileNetV2's `[-1, 1]` rescaling internally. The default location is `backend/models/plant_disease_mobilenetv2`; set `FASALSETU_DISEASE_MODEL_DIR` to use another directory.

**No disease weights are currently installed or downloaded.** The Crop Doctor therefore stays in **DEMO MODE · NO MODEL**, disables analysis, and `/api/crop-diagnosis` returns an explicit 503 for valid images. The output-contract tests use a test double only; they are not model evaluations.

### Research and licensing decision

- The [PlantVillage dataset page](https://huggingface.co/datasets/mohanty/PlantVillage) maintained by the dataset authors declares **CC BY-SA 3.0**, describes 54,306 controlled-condition images across 14 crop species, and publishes 38 classes. The data-preparation command requires an explicit license acknowledgement. Preserve attribution and review share-alike obligations before redistributing any dataset-derived model.
- [`Daksh159/plant-disease-mobilenetv2`](https://huggingface.co/Daksh159/plant-disease-mobilenetv2) declares Apache-2.0, but its repository API lists only a `.pth` and README although the README claims a separate `class_names.json`; its reported accuracy is not accompanied by reproducible evaluation code, and the underlying augmented dataset licensing is not clear. It was not downloaded.
- [`linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`](https://huggingface.co/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification) declares `license: other`, so the checkpoint's terms are unclear. It was not downloaded.
- Google's [Hugging Face MobileNetV2](https://huggingface.co/google/mobilenet_v2_1.0_224) is an ImageNet classifier, not a crop disease model, and its card also declares `license: other`. It cannot directly classify the PlantVillage disease classes.
- Keras documents MobileNetV2's 224×224 input and `[-1, 1]` preprocessing ([API](https://www.tensorflow.org/api_docs/python/tf/keras/applications/MobileNetV2), [preprocessing](https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet_v2/preprocess_input)). The [Keras source code](https://github.com/keras-team/keras/blob/master/LICENSE) is Apache-2.0, but that does **not** by itself establish the separate ImageNet checkpoint or ImageNet data terms. The training script downloads official Keras ImageNet weights only when `--imagenet-weights` is explicitly supplied; review the checkpoint/data terms before using or distributing them. No weights were downloaded for this implementation.

### Train a PlantVillage model

Training requires an ML-capable Python environment and about 2 GB or more of dataset storage, plus space for extracted images and model output:

```powershell
pip install -r requirements-ml.txt
python -m backend.prepare_plantvillage --accept-cc-by-sa --output-dir data\plantvillage
python -m backend.train_disease_model --dataset-dir data\plantvillage --imagenet-weights
```

The preparation script downloads the authors' PlantVillage RGB train/test splits and deterministically separates 20% of training `leaf_id` groups into validation, keeping images of the same leaf together. The training command uses an ImageNet MobileNetV2 backbone, a new 38-class softmax head, fine-tuning, and the held-out dataset test split; it saves measured test metrics and class ordering alongside the Keras model. `--imagenet-weights` is an explicit opt-in to a download, not a license grant. If the checkpoint/data terms have not been reviewed, omit the flag; that run uses random initialization and is **not** transfer learning.

The resulting model is still a research/demo classifier, not validated for field conditions. PlantVillage images have controlled backgrounds; test metrics and softmax scores do not establish on-farm accuracy. Collect and evaluate representative Indian field images and have local agricultural experts review recommendations before relying on or distributing a model. The curated guidance deliberately avoids pesticide dosage.

## Important limitations

- The default weather location is Pune, Maharashtra. A location selected through Weather Intelligence is stored in SQLite and restored after refresh; it is separate from the farmer-entered farm address.
- Weather requires internet access to Open-Meteo. API/network errors are shown rather than replaced with fictional measurements.
- Crop disease predictions require an installed model artifact; none is included. Only the exact PlantVillage 38-class MobileNetV2 metadata format generated by the training script is accepted. Even after training, field evaluation is required before practical use.
- Advisory output is conservative rule-based education, not crop-specific professional advice. Live forecast rules use Open-Meteo; when forecast data is unavailable, the response says so and omits weather-based inference.
- Generative assistant use requires a provider account, network access and backend-only credentials. Without them the curated fallback remains available. Provider requests may include the current farm crop, soil, growth stage and size, but not the farmer's name.
- Weather risk rules are informational and not a replacement for IMD alerts, field inspection or agricultural extension advice. The dashboard chart counts saved history only; this project has no sensor integration.
- SQLite represents one local farm profile. There is no login, multi-farmer tenancy or cloud synchronization.

## API

- `GET /api/health`
- `GET /api/weather?latitude=18.5204&longitude=73.8567`
- `GET|PUT /api/weather/location`
- `GET /api/locations?name=Pune`
- `GET|PUT /api/farm`
- `GET|POST|PUT|DELETE /api/farm/crops`
- `GET|POST /api/farm/activities`
- `GET /api/history`
- `GET /api/dashboard/summary`
- `POST /api/advisory`
- `GET /api/assistant/status`
- `POST /api/assistant`
- `GET /api/crop-diagnosis/status` (reports model availability; does not fabricate a fallback)
- `POST /api/crop-diagnosis` (multipart field `image`, optional `language=en|hi`; returns prediction only when a compatible model is installed)

Interactive API documentation is available at `http://localhost:8000/docs`.

Run the backend regression suite with `python -m unittest backend.test_application backend.test_crop_disease`; both suites use temporary SQLite files and mocked external providers. Build the frontend with `npm run build`.
