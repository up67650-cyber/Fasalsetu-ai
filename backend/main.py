import json
import logging
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from .crop_disease import (
    ImageTooLargeError,
    InvalidLeafImageError,
    ModelUnavailableError,
    SUPPORTED_IMAGE_TYPES,
    UnsupportedImageError,
    classify_leaf,
    decode_leaf_image,
    get_disease_model,
)


DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(Path(__file__).with_name("fasalsetu.db"))))
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    app.state.database_path = str(DATABASE_PATH)
    yield


DEFAULT_CORS_ORIGINS = (
    "https://fasalsetu-ai-frontend.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def get_cors_origins():
    configured_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    return list(dict.fromkeys([*DEFAULT_CORS_ORIGINS, *configured_origins]))


app = FastAPI(title="FasalSetu AI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def connect_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_db():
    with connect_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS farm_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            farmer_name TEXT NOT NULL DEFAULT '',
            location TEXT NOT NULL DEFAULT 'Pune, Maharashtra',
            farm_size_acres REAL NOT NULL DEFAULT 2,
            crop TEXT NOT NULL DEFAULT 'Wheat',
            soil_type TEXT NOT NULL DEFAULT 'Loamy',
            growth_stage TEXT NOT NULL DEFAULT 'Vegetative',
            weather_location_name TEXT NOT NULL DEFAULT 'Pune, Maharashtra, India',
            weather_latitude REAL NOT NULL DEFAULT 18.5204,
            weather_longitude REAL NOT NULL DEFAULT 73.8567
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL,
            activity_type TEXT NOT NULL DEFAULT 'other',
            crop TEXT,
            metadata_json TEXT NOT NULL DEFAULT '{}'
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS farm_crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT NOT NULL,
            variety TEXT NOT NULL DEFAULT '',
            area_acres REAL,
            planting_date TEXT,
            growth_stage TEXT NOT NULL DEFAULT 'Sowing',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")
        _add_columns(db, "farm_profile", {
            "weather_location_name": "TEXT NOT NULL DEFAULT 'Pune, Maharashtra, India'",
            "weather_latitude": "REAL NOT NULL DEFAULT 18.5204",
            "weather_longitude": "REAL NOT NULL DEFAULT 73.8567",
        })
        _add_columns(db, "history", {
            "activity_type": "TEXT NOT NULL DEFAULT 'other'",
            "crop": "TEXT",
            "metadata_json": "TEXT NOT NULL DEFAULT '{}'",
        })
        db.execute("CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_history_type_created ON history(activity_type, created_at)")
        db.execute("INSERT OR IGNORE INTO farm_profile (id) VALUES (1)")


def _add_columns(db: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    existing = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
    for name, definition in columns.items():
        if name not in existing:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def record_history(
    db: sqlite3.Connection,
    activity_type: str,
    title: str,
    details: str,
    crop: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    db.execute(
        """INSERT INTO history (title, details, created_at, activity_type, crop, metadata_json)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            title,
            details,
            datetime.now(timezone.utc).isoformat(),
            activity_type,
            crop,
            json.dumps(metadata or {}, ensure_ascii=False),
        ),
    )


class FarmProfile(BaseModel):
    farmer_name: str = Field(default="", max_length=100)
    location: str = Field(default="Pune, Maharashtra", min_length=2, max_length=160)
    farm_size_acres: float = Field(default=2, gt=0, le=100000)
    crop: str = Field(default="Wheat", min_length=1, max_length=60)
    soil_type: str = Field(default="Loamy", min_length=1, max_length=60)
    growth_stage: str = Field(default="Vegetative", min_length=1, max_length=60)


class WeatherLocation(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AdvisoryRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=60)
    soil_type: str = Field(min_length=1, max_length=60)
    location: str = Field(min_length=2, max_length=160)
    growth_stage: str = Field(min_length=1, max_length=60)
    farm_size_acres: float = Field(default=2, gt=0, le=100000)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    language: str = Field(default="en", pattern="^(en|hi)$")


class AssistantRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    language: str = Field(default="en", pattern="^(en|hi)$")


class FarmCropRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=60)
    variety: str = Field(default="", max_length=100)
    area_acres: Optional[float] = Field(default=None, gt=0, le=100000)
    planting_date: Optional[date] = None
    growth_stage: str = Field(default="Sowing", min_length=1, max_length=60)


class FarmActivityRequest(BaseModel):
    activity_type: Literal["planting", "irrigation", "fertilizing", "scouting", "harvest", "other"]
    details: str = Field(min_length=2, max_length=1000)
    crop: Optional[str] = Field(default=None, max_length=60)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "FasalSetu AI API"}


@app.get("/api/farm")
def get_farm():
    with connect_db() as db:
        row = db.execute(
            """SELECT farmer_name, location, farm_size_acres, crop, soil_type, growth_stage
               FROM farm_profile WHERE id=1"""
        ).fetchone()
    return dict(row)


@app.put("/api/farm")
def save_farm(profile: FarmProfile):
    normalized_location = profile.location.strip()
    if len(normalized_location) < 2:
        raise HTTPException(status_code=422, detail="Enter a valid farm location.")
    with connect_db() as db:
        db.execute(
            """UPDATE farm_profile
               SET farmer_name=?, location=?, farm_size_acres=?, crop=?, soil_type=?, growth_stage=?
               WHERE id=1""",
            (
                profile.farmer_name.strip(),
                normalized_location,
                profile.farm_size_acres,
                profile.crop.strip(),
                profile.soil_type.strip(),
                profile.growth_stage.strip(),
            ),
        )
        record_history(
            db,
            "farm_profile",
            "Farm profile updated",
            f"{profile.crop.strip()} · {profile.farm_size_acres:g} acres · {normalized_location}",
            profile.crop.strip(),
        )
        row = db.execute(
            """SELECT farmer_name, location, farm_size_acres, crop, soil_type, growth_stage
               FROM farm_profile WHERE id=1"""
        ).fetchone()
    return dict(row)


@app.get("/api/weather/location")
def get_weather_location():
    with connect_db() as db:
        row = db.execute(
            """SELECT weather_location_name AS name, weather_latitude AS latitude,
                      weather_longitude AS longitude
               FROM farm_profile WHERE id=1"""
        ).fetchone()
    return dict(row)


@app.put("/api/weather/location")
def save_weather_location(location: WeatherLocation):
    name = location.name.strip()
    if len(name) < 2:
        raise HTTPException(status_code=422, detail="Enter a valid forecast location.")
    with connect_db() as db:
        db.execute(
            """UPDATE farm_profile
               SET weather_location_name=?, weather_latitude=?, weather_longitude=?
               WHERE id=1""",
            (name, location.latitude, location.longitude),
        )
        record_history(db, "weather_location", "Forecast location updated", name)
    return {"name": name, "latitude": location.latitude, "longitude": location.longitude}


def _history_entry(row: sqlite3.Row) -> dict:
    entry = dict(row)
    try:
        entry["metadata"] = json.loads(entry.pop("metadata_json", "{}"))
    except (TypeError, json.JSONDecodeError):
        entry["metadata"] = {}
    return entry


@app.get("/api/history")
def get_history(
    activity_type: Optional[str] = Query(default=None, max_length=40),
    limit: int = Query(default=50, ge=1, le=100),
):
    with connect_db() as db:
        if activity_type:
            rows = db.execute(
                """SELECT id, title, details, created_at, activity_type, crop, metadata_json
                   FROM history WHERE activity_type=? ORDER BY id DESC LIMIT ?""",
                (activity_type, limit),
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT id, title, details, created_at, activity_type, crop, metadata_json
                   FROM history ORDER BY id DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    return {"entries": [_history_entry(row) for row in rows]}


@app.get("/api/farm/crops")
def get_farm_crops():
    with connect_db() as db:
        rows = db.execute(
            """SELECT id, crop, variety, area_acres, planting_date, growth_stage,
                      created_at, updated_at
               FROM farm_crops ORDER BY id DESC"""
        ).fetchall()
    return {"crops": [dict(row) for row in rows]}


@app.post("/api/farm/crops", status_code=201)
def add_farm_crop(crop: FarmCropRequest):
    crop_name = crop.crop.strip()
    if not crop_name:
        raise HTTPException(status_code=422, detail="Enter a crop name.")
    now = datetime.now(timezone.utc).isoformat()
    with connect_db() as db:
        cursor = db.execute(
            """INSERT INTO farm_crops
               (crop, variety, area_acres, planting_date, growth_stage, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                crop_name,
                crop.variety.strip(),
                crop.area_acres,
                crop.planting_date.isoformat() if crop.planting_date else None,
                crop.growth_stage.strip(),
                now,
                now,
            ),
        )
        crop_id = cursor.lastrowid
        record_history(
            db,
            "crop_added",
            "Crop added",
            f"{crop_name} · {crop.growth_stage.strip()}",
            crop_name,
            {"crop_id": crop_id, "area_acres": crop.area_acres},
        )
        row = db.execute("SELECT * FROM farm_crops WHERE id=?", (crop_id,)).fetchone()
    return dict(row)


@app.put("/api/farm/crops/{crop_id}")
def update_farm_crop(crop_id: int, crop: FarmCropRequest):
    crop_name = crop.crop.strip()
    if not crop_name:
        raise HTTPException(status_code=422, detail="Enter a crop name.")
    now = datetime.now(timezone.utc).isoformat()
    with connect_db() as db:
        cursor = db.execute(
            """UPDATE farm_crops
               SET crop=?, variety=?, area_acres=?, planting_date=?, growth_stage=?, updated_at=?
               WHERE id=?""",
            (
                crop_name,
                crop.variety.strip(),
                crop.area_acres,
                crop.planting_date.isoformat() if crop.planting_date else None,
                crop.growth_stage.strip(),
                now,
                crop_id,
            ),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Farm crop was not found.")
        record_history(
            db,
            "crop_updated",
            "Crop details updated",
            f"{crop_name} · {crop.growth_stage.strip()}",
            crop_name,
            {"crop_id": crop_id, "area_acres": crop.area_acres},
        )
        row = db.execute("SELECT * FROM farm_crops WHERE id=?", (crop_id,)).fetchone()
    return dict(row)


@app.delete("/api/farm/crops/{crop_id}")
def delete_farm_crop(crop_id: int):
    with connect_db() as db:
        row = db.execute("SELECT crop FROM farm_crops WHERE id=?", (crop_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Farm crop was not found.")
        db.execute("DELETE FROM farm_crops WHERE id=?", (crop_id,))
        record_history(
            db,
            "crop_removed",
            "Crop removed",
            str(row["crop"]),
            str(row["crop"]),
            {"crop_id": crop_id},
        )
    return {"deleted": True, "id": crop_id}


@app.get("/api/farm/activities")
def get_farm_activities(limit: int = Query(default=50, ge=1, le=100)):
    with connect_db() as db:
        rows = db.execute(
            """SELECT id, title, details, created_at, activity_type, crop, metadata_json
               FROM history WHERE activity_type='farm_activity' ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return {"activities": [_history_entry(row) for row in rows]}


@app.post("/api/farm/activities", status_code=201)
def add_farm_activity(activity: FarmActivityRequest):
    details = activity.details.strip()
    if len(details) < 2:
        raise HTTPException(status_code=422, detail="Add a short description of the activity.")
    titles = {
        "planting": "Planting recorded",
        "irrigation": "Irrigation recorded",
        "fertilizing": "Fertilizer activity recorded",
        "scouting": "Field scouting recorded",
        "harvest": "Harvest recorded",
        "other": "Farm activity recorded",
    }
    with connect_db() as db:
        record_history(
            db,
            "farm_activity",
            titles[activity.activity_type],
            details,
            activity.crop.strip() if activity.crop else None,
            {"activity_type": activity.activity_type},
        )
        row = db.execute("SELECT * FROM history ORDER BY id DESC LIMIT 1").fetchone()
    return _history_entry(row)


@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=6)
    labels = [first_day + timedelta(days=index) for index in range(7)]
    with connect_db() as db:
        counts = db.execute(
            """SELECT COUNT(*) AS total,
                      SUM(CASE WHEN activity_type='farm_activity' THEN 1 ELSE 0 END) AS activities,
                      SUM(CASE WHEN activity_type='advisory' THEN 1 ELSE 0 END) AS advisories,
                      SUM(CASE WHEN activity_type='crop_diagnosis' THEN 1 ELSE 0 END) AS diagnoses
               FROM history"""
        ).fetchone()
        by_day = db.execute(
            """SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS count
               FROM history WHERE substr(created_at, 1, 10) >= ?
               GROUP BY substr(created_at, 1, 10)""",
            (first_day.isoformat(),),
        ).fetchall()
        latest = db.execute(
            """SELECT id, title, details, created_at, crop, metadata_json
               FROM history WHERE activity_type='crop_diagnosis' ORDER BY id DESC LIMIT 1"""
        ).fetchone()
        farm_crop_count = db.execute("SELECT COUNT(*) FROM farm_crops").fetchone()[0]
    activity_counts = {row["day"]: row["count"] for row in by_day}
    latest_diagnosis = None
    if latest:
        try:
            metadata = json.loads(latest["metadata_json"])
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        latest_diagnosis = {
            "id": latest["id"],
            "title": latest["title"],
            "details": latest["details"],
            "created_at": latest["created_at"],
            "crop": latest["crop"],
            "prediction": metadata.get("prediction"),
        }
    return {
        "totals": {
            "history": counts["total"] or 0,
            "activities": counts["activities"] or 0,
            "advisories": counts["advisories"] or 0,
            "diagnoses": counts["diagnoses"] or 0,
            "farm_crops": farm_crop_count,
        },
        "daily_activity": [
            {
                "date": day.isoformat(),
                "label": day.strftime("%a"),
                "count": activity_counts.get(day.isoformat(), 0),
            }
            for day in labels
        ],
        "latest_diagnosis": latest_diagnosis,
    }


def fetch_weather(latitude: float, longitude: float, language: str = "en") -> dict:
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise HTTPException(status_code=422, detail="Latitude or longitude is out of range.")
    query = urlencode({
        "latitude": latitude, "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "timezone": "auto", "forecast_days": 7,
    })
    try:
        with urlopen(f"https://api.open-meteo.com/v1/forecast?{query}", timeout=8) as response:
            data = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        LOGGER.warning("Open-Meteo forecast request failed: %s", error)
        raise HTTPException(
            status_code=503,
            detail="Live weather is unavailable. Check your connection and try again.",
        ) from error
    current = data.get("current", {})
    daily = data.get("daily", {})
    if not current or not daily:
        raise HTTPException(status_code=503, detail="Open-Meteo returned incomplete forecast data.")
    risks = []
    high_temps = daily.get("temperature_2m_max", [])
    rain = daily.get("precipitation_sum", [])
    if any(value is not None and value >= 38 for value in high_temps):
        risks.append({
            "title": "High temperature forecast" if language == "en" else "उच्च तापमान का अनुमान",
            "message": (
                "A hot day is forecast. Check crop water needs and avoid spraying during peak heat."
                if language == "en"
                else "गर्म दिन का अनुमान है। फसल की पानी की जरूरत जांचें और तेज गर्मी में छिड़काव न करें।"
            ),
            "severity": "Moderate" if language == "en" else "मध्यम",
        })
    if any(value is not None and value >= 40 for value in rain):
        risks.append({
            "title": "Heavy rainfall possible" if language == "en" else "भारी वर्षा की संभावना",
            "message": (
                "Heavy rainfall is in the forecast. Check drainage and follow local weather alerts."
                if language == "en"
                else "भारी वर्षा का अनुमान है। जल निकासी जांचें और स्थानीय मौसम चेतावनियों का पालन करें।"
            ),
            "severity": "Moderate" if language == "en" else "मध्यम",
        })
    wind = current.get("wind_speed_10m")
    if wind is not None and wind >= 35:
        risks.append({
            "title": "Strong wind conditions" if language == "en" else "तेज हवा की स्थिति",
            "message": (
                "Secure loose equipment and postpone work at height. Follow local warnings."
                if language == "en"
                else "ढीले उपकरण सुरक्षित करें और ऊंचाई पर काम टालें। स्थानीय चेतावनियों का पालन करें।"
            ),
            "severity": "Moderate" if language == "en" else "मध्यम",
        })
    current["weather_description"] = weather_description(current.get("weather_code"), language)
    rain_48h = sum(value for value in rain[:2] if value is not None)
    if rain_48h >= 10:
        irrigation_guidance = (
            "The 2-day forecast totals at least 10 mm of rain. Check field drainage and root-zone moisture before irrigating."
            if language == "en"
            else "अगले 2 दिनों में कम से कम 10 मिमी वर्षा का अनुमान है। सिंचाई से पहले जल निकासी और जड़ क्षेत्र की नमी जांचें।"
        )
    else:
        irrigation_guidance = (
            "Forecast rainfall is below 10 mm over the next 2 days. Check root-zone soil moisture before deciding whether to irrigate."
            if language == "en"
            else "अगले 2 दिनों में 10 मिमी से कम वर्षा का अनुमान है। सिंचाई का निर्णय लेने से पहले जड़ क्षेत्र की मिट्टी की नमी जांचें।"
        )
    return {
        "current": current,
        "daily": daily,
        "risks": risks,
        "irrigation_guidance": irrigation_guidance,
        "source": "Open-Meteo",
    }


@app.get("/api/weather")
def get_weather(
    latitude: float = 18.5204,
    longitude: float = 73.8567,
    language: str = Query(default="en", pattern="^(en|hi)$"),
):
    return fetch_weather(latitude, longitude, language)


@app.get("/api/locations")
def search_locations(name: str = Query(min_length=2, max_length=100)):
    query = urlencode({"name": name.strip(), "count": 8, "language": "en", "format": "json"})
    try:
        with urlopen(f"https://geocoding-api.open-meteo.com/v1/search?{query}", timeout=8) as response:
            data = json.loads(response.read())
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail=f"Location search is unavailable: {error}") from error
    locations = []
    for result in data.get("results", []):
        display_name = ", ".join(
            part for part in (result.get("name"), result.get("admin1"), result.get("country"))
            if part
        )
        locations.append({
            "name": display_name,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        })
    return {"results": locations}


def weather_description(code: Optional[int], language: str = "en"):
    if code is None:
        description = "Conditions unavailable"
    elif code == 0:
        description = "Clear sky"
    elif code in (1, 2):
        description = "Mainly clear, partly cloudy"
    elif code == 3:
        description = "Overcast"
    elif code in (45, 48):
        description = "Fog"
    elif code in (51, 53, 55, 56, 57):
        description = "Drizzle"
    elif code in (61, 63, 65, 66, 67, 80, 81, 82):
        description = "Rain showers"
    elif code in (71, 73, 75, 77, 85, 86):
        description = "Snow"
    elif code in (95, 96, 99):
        description = "Thunderstorm"
    else:
        description = "Variable conditions"
    hindi = {
        "Conditions unavailable": "मौसम की जानकारी उपलब्ध नहीं",
        "Clear sky": "साफ आसमान",
        "Mainly clear, partly cloudy": "मुख्यतः साफ, कुछ बादल",
        "Overcast": "बादल छाए हुए",
        "Fog": "कोहरा",
        "Drizzle": "बूंदाबांदी",
        "Rain showers": "बारिश की बौछारें",
        "Snow": "बर्फबारी",
        "Thunderstorm": "आंधी-तूफान",
        "Variable conditions": "बदलता मौसम",
    }
    return hindi[description] if language == "hi" else description


@app.post("/api/advisory")
def get_advisory(request: AdvisoryRequest):
    if (request.latitude is None) != (request.longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Provide both latitude and longitude for forecast-aware guidance.",
        )
    weather = None
    weather_error = None
    if request.latitude is not None and request.longitude is not None:
        try:
            weather = fetch_weather(request.latitude, request.longitude, request.language)
        except HTTPException as error:
            if error.status_code != 503:
                raise
            weather_error = (
                "लाइव मौसम उपलब्ध नहीं था; मौसम-आधारित सलाह शामिल नहीं की गई।"
                if request.language == "hi"
                else error.detail
            )

    crop = request.crop.strip()
    stage = request.growth_stage.strip()
    is_hindi = request.language == "hi"
    rainfall = weather.get("daily", {}).get("precipitation_sum", []) if weather else []
    rain_48h = sum(value for value in rainfall[:2] if value is not None)
    if not weather:
        irrigation = (
            f"At the {stage.lower()} stage, check root-zone moisture before watering and avoid irrigation when soil is saturated. Live forecast data was unavailable."
            if not is_hindi
            else f"{stage} अवस्था में पानी देने से पहले जड़ क्षेत्र की नमी जांचें और मिट्टी संतृप्त होने पर सिंचाई न करें। लाइव मौसम पूर्वानुमान उपलब्ध नहीं था।"
        )
    elif rain_48h >= 10:
        irrigation = (
            f"The 2-day Open-Meteo forecast totals {rain_48h:.1f} mm. Check drainage and root-zone moisture before irrigating."
            if not is_hindi
            else f"Open-Meteo के 2-दिन के पूर्वानुमान में {rain_48h:.1f} मिमी वर्षा है। सिंचाई से पहले जल निकासी और जड़ क्षेत्र की नमी जांचें।"
        )
    else:
        irrigation = (
            f"The 2-day forecast totals {rain_48h:.1f} mm. Check root-zone moisture; do not decide from a calendar alone."
            if not is_hindi
            else f"2-दिन के पूर्वानुमान में {rain_48h:.1f} मिमी वर्षा है। केवल कैलेंडर के आधार पर नहीं, जड़ क्षेत्र की नमी देखकर निर्णय लें।"
        )
    normalized_stage = stage.casefold()
    if normalized_stage in {"sowing", "seedling"}:
        stage_detail = (
            "Maintain even moisture for establishment while avoiding waterlogging; use locally recommended seed and planting depth."
            if not is_hindi
            else "स्थापना के लिए मिट्टी में समान नमी रखें, जलभराव से बचें और स्थानीय रूप से अनुशंसित बीज व बुवाई गहराई अपनाएं।"
        )
    elif normalized_stage in {"flowering", "fruiting"}:
        stage_detail = (
            "Inspect the crop frequently during this sensitive stage and avoid moisture stress; use local crop-stage guidance for timing."
            if not is_hindi
            else "इस संवेदनशील अवस्था में फसल का नियमित निरीक्षण करें और नमी की कमी से बचें; समय के लिए स्थानीय फसल-अवस्था सलाह लें।"
        )
    elif normalized_stage == "harvest":
        stage_detail = (
            "Check crop-specific maturity signs and the local harvest window; keep harvested produce dry and follow safe storage guidance."
            if not is_hindi
            else "फसल के अनुसार पकने के संकेत और स्थानीय कटाई समय जांचें; उपज सूखी रखें और सुरक्षित भंडारण सलाह अपनाएं।"
        )
    else:
        stage_detail = (
            "Record crop growth and inspect for lodging, water stress or unusual symptoms; compare with local crop-stage guidance."
            if not is_hindi
            else "फसल की वृद्धि दर्ज करें और गिरने, पानी की कमी या असामान्य लक्षणों की जांच करें; स्थानीय फसल-अवस्था सलाह से तुलना करें।"
        )
    result = {
        "crop": crop,
        "growth_stage": stage,
        "recommendations": [
            {
                "title": "Irrigation check" if not is_hindi else "सिंचाई की जांच",
                "detail": irrigation,
            },
            {
                "title": "Soil-test-based nutrients" if not is_hindi else "मिट्टी जांच के आधार पर पोषण",
                "detail": (
                    f"For {request.soil_type.lower()} soil, use a current soil test and state crop recommendations. This advisory does not calculate fertilizer rates."
                    if not is_hindi
                    else f"{request.soil_type} मिट्टी के लिए हाल की मिट्टी जांच और राज्य की फसल सलाह अपनाएं। यह सलाह उर्वरक की मात्रा निर्धारित नहीं करती।"
                ),
            },
            {
                "title": "Field scouting" if not is_hindi else "खेत का निरीक्षण",
                "detail": (
                    f"Inspect several parts of the {crop} field for changing leaf, stem or soil symptoms. Seek local confirmation before treating suspected pests or disease."
                    if not is_hindi
                    else f"{crop} खेत के अलग-अलग हिस्सों में पत्तियों, तनों और मिट्टी के बदलाव देखें। कीट या रोग के उपचार से पहले स्थानीय पुष्टि लें।"
                ),
            },
            {
                "title": "Growth-stage action" if not is_hindi else "वृद्धि अवस्था के अनुसार काम",
                "detail": stage_detail,
            },
            {
                "title": "Farm planning" if not is_hindi else "खेत की योजना",
                "detail": (
                    f"Your recorded area is {request.farm_size_acres:g} acres. Use it to plan field work; do not derive input quantities from area without the crop label or local package of practices."
                    if not is_hindi
                    else f"दर्ज खेत का क्षेत्र {request.farm_size_acres:g} एकड़ है। इसका उपयोग काम की योजना के लिए करें; फसल लेबल या स्थानीय कृषि पद्धति के बिना इनपुट की मात्रा तय न करें।"
                ),
            },
        ],
        "summary": (
            f"General guidance for {crop} at the {stage.lower()} stage in {request.location.strip()} on {request.soil_type.lower()} soil."
            if not is_hindi
            else f"{request.location.strip()} में {request.soil_type} मिट्टी पर {crop} की {stage} अवस्था के लिए सामान्य सलाह।"
        ),
        "disclaimer": (
            "Educational, rule-based guidance—not a diagnosis or pesticide prescription. Follow current state/ICAR crop practices and consult your KVK or agriculture extension officer."
            if not is_hindi
            else "यह शैक्षिक, नियम-आधारित सलाह है—निदान या कीटनाशक निर्देश नहीं। राज्य/ICAR की वर्तमान फसल पद्धति अपनाएं और KVK या कृषि विस्तार अधिकारी से सलाह लें।"
        ),
        "label": "Rule-based guidance — not an AI prediction" if not is_hindi else "नियम-आधारित सलाह — AI पूर्वानुमान नहीं",
        "weather_used": weather is not None,
        "references": [
            "https://soilhealth.dac.gov.in/",
            "https://open-meteo.com/en/docs",
            "Local Krishi Vigyan Kendra (KVK) / state package of practices",
        ],
        "farm_size_acres": request.farm_size_acres,
    }
    if weather_error:
        result["weather_note"] = weather_error
    with connect_db() as db:
        record_history(
            db,
            "advisory",
            "Crop advisory generated",
            f"{crop} · {stage} · {request.location.strip()}",
            crop,
            result,
        )
    return result


def _fallback_answer(question: str, language: str) -> str:
    lowered = question.casefold()
    is_hindi = language == "hi"
    topics = (
        (
            ("yellow", "leaf", "पत्ता", "पत्ते", "पीला", "पीली", "रोग", "disease"),
            "पत्तियों का पीला होना पानी, पोषक तत्व, कीट या रोग सहित कई कारणों से हो सकता है। पहले मिट्टी की नमी और लक्षणों के फैलाव की जांच करें। उपचार से पहले स्थानीय कृषि विशेषज्ञ से पहचान की पुष्टि लें।"
            if is_hindi
            else "Yellowing or leaf symptoms can have several causes, including water or nutrient stress, pests, or disease. Check soil moisture and whether symptoms are spreading; get local confirmation before treating.",
        ),
        (
            ("irrigat", "water", "सिंच", "पानी"),
            "सिंचाई से पहले जड़ क्षेत्र की मिट्टी की नमी और स्थानीय वर्षा पूर्वानुमान जांचें। फसल अवस्था और मिट्टी के अनुसार निर्णय लें तथा जलभराव से बचें।"
            if is_hindi
            else "Check root-zone soil moisture and the local rainfall forecast before irrigating. Base timing on crop stage and soil conditions, and avoid waterlogging.",
        ),
        (
            ("soil", "fertiliz", "मिट्टी", "खाद", "उर्वरक", "nutrient"),
            "पोषक तत्वों का निर्णय मिट्टी जांच और स्थानीय फसल सलाह के आधार पर लें। केवल पत्तियों के रंग या सामान्य अनुसूची से उर्वरक की मात्रा तय न करें।"
            if is_hindi
            else "Base nutrient decisions on a soil test and local crop recommendations. Do not determine fertilizer quantities from leaf color or a generic schedule.",
        ),
        (
            ("pest", "कीट"),
            "खेत का निरीक्षण करें और कीट की सही पहचान स्थानीय विशेषज्ञ से कराएं। बिना पुष्टि के कीटनाशक न लगाएं; सुरक्षित उपयोग के लिए उत्पाद लेबल और स्थानीय नियमों का पालन करें।"
            if is_hindi
            else "Scout the crop and confirm pest identity with a local expert. Do not apply a pesticide without confirmation; follow the product label and local rules for any approved use.",
        ),
    )
    for words, answer in topics:
        if any(word in lowered for word in words):
            return answer
    return (
        "यह सहायक खेती से जुड़े सामान्य प्रश्नों में मदद करता है। फसल, मिट्टी और स्थानीय मौसम के अनुसार निर्णय लें; गंभीर समस्या में अपने कृषि विज्ञान केंद्र (KVK) या कृषि विस्तार अधिकारी से संपर्क करें।"
        if is_hindi
        else "I can help with general farming questions. Consider your crop, soil and local weather; contact your Krishi Vigyan Kendra (KVK) or agriculture extension officer for a serious field issue."
    )


def _generate_assistant_answer(
    question: str, language: str, farm: dict
) -> tuple[Optional[str], Optional[str]]:
    api_key = os.getenv("FARM_ASSISTANT_API_KEY", "").strip()
    if not api_key:
        return None, "AI provider is not configured"
    base_url = os.getenv("FARM_ASSISTANT_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("FARM_ASSISTANT_MODEL", "gpt-4o-mini").strip()
    system_prompt = (
        "You are FasalSetu, an agricultural information assistant for Indian farmers. "
        "Answer only farming/agriculture questions, in the user's requested language. "
        "Be cautious and distinguish general information from field diagnosis. Never give pesticide dosage or unsafe chemical instructions. "
        "Ask for missing context where needed and recommend a local KVK/agriculture extension officer for consequential decisions. "
        "Use the supplied farm context only when relevant."
    )
    context = {
        "crop": farm.get("crop"),
        "soil_type": farm.get("soil_type"),
        "growth_stage": farm.get("growth_stage"),
        "farm_size_acres": farm.get("farm_size_acres"),
    }
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Respond in {'Hindi' if language == 'hi' else 'English'}. "
                    f"Farm context: {json.dumps(context)}\nQuestion: {question}"
                ),
            },
        ],
    }
    provider_request = Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(provider_request, timeout=20) as response:
            result = json.loads(response.read())
        answer = result["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("AI provider returned an empty answer")
    except (
        HTTPError,
        URLError,
        TimeoutError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
        ValueError,
    ) as error:
        LOGGER.warning("Farm assistant provider request failed: %s", error)
        return None, "AI provider is unavailable"
    return answer.strip(), model


@app.get("/api/assistant/status")
def assistant_status():
    return {
        "generative_available": bool(os.getenv("FARM_ASSISTANT_API_KEY", "").strip()),
        "provider": os.getenv("FARM_ASSISTANT_PROVIDER", "OpenAI-compatible"),
        "model": os.getenv("FARM_ASSISTANT_MODEL", "gpt-4o-mini"),
    }


@app.post("/api/assistant")
def assistant(request: AssistantRequest):
    question = request.question.strip()
    with connect_db() as db:
        farm = dict(
            db.execute(
                """SELECT crop, soil_type, growth_stage, farm_size_acres
                   FROM farm_profile WHERE id=1"""
            ).fetchone()
        )
    answer, provider_result = _generate_assistant_answer(question, request.language, farm)
    if answer is not None:
        label = f"AI-generated · {provider_result} · verify locally"
        source = "configured_provider"
    else:
        answer = _fallback_answer(question, request.language)
        label = (
            "Curated fallback · AI provider is not configured"
            if provider_result == "AI provider is not configured"
            else "Curated fallback · AI provider is unavailable"
        )
        source = "curated_fallback"
    with connect_db() as db:
        record_history(
            db,
            "assistant",
            "Farm assistant used",
            question[:180],
            farm.get("crop"),
            {"source": source, "label": label},
        )
    return {"answer": answer, "label": label, "source": source}


@app.get("/api/crop-diagnosis/status")
async def crop_diagnosis_status():
    try:
        bundle = await run_in_threadpool(get_disease_model)
    except ModelUnavailableError as error:
        return {"available": False, "message": str(error)}
    if bundle is None:
        return {
            "available": False,
            "message": "No trained disease model is installed. No predictions will be made.",
        }
    return {
        "available": True,
        "message": "A crop disease model is loaded.",
        "model": {
            "name": bundle.metadata.get("model_name", "MobileNetV2 plant disease classifier"),
            "dataset": bundle.metadata.get("dataset", "Not specified"),
            "class_count": len(bundle.metadata["classes"]),
        },
    }


@app.post("/api/crop-diagnosis")
async def crop_diagnosis(
    image: UploadFile = File(...),
    language: str = Query(default="en", pattern="^(en|hi)$"),
):
    if image.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG or WebP image.")
    content = await image.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")
    try:
        pixels = await run_in_threadpool(decode_leaf_image, content, image.content_type)
    except UnsupportedImageError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except ImageTooLargeError as error:
        raise HTTPException(status_code=413, detail=str(error)) from error
    except InvalidLeafImageError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    try:
        bundle = await run_in_threadpool(get_disease_model)
        if bundle is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Crop diagnosis is unavailable: no trained disease model is configured. "
                    "No prediction was made."
                ),
            )
        result = await run_in_threadpool(classify_leaf, pixels, bundle, language)
        prediction = result["prediction"]
        with connect_db() as db:
            record_history(
                db,
                "crop_diagnosis",
                "Crop diagnosis completed",
                (
                    f"{prediction['crop']} · {prediction['disease']} · "
                    f"{prediction['confidence']:.3f} score"
                ),
                prediction["crop"],
                result,
            )
        return result
    except ModelUnavailableError as error:
        LOGGER.error("Crop diagnosis is unavailable: %s", error)
        raise HTTPException(status_code=503, detail=f"{error} No prediction was made.") from error
