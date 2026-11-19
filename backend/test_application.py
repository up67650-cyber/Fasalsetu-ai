import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from fastapi.testclient import TestClient

from backend import main


def weather_payload(rain=None, high_temps=None, wind=8):
    rainfall = rain or [0, 0, 0, 0, 0, 0, 0]
    temps = high_temps or [28, 29, 30, 31, 32, 33, 34]
    return {
        "current": {
            "temperature_2m": 27.1,
            "relative_humidity_2m": 64,
            "apparent_temperature": 28.0,
            "precipitation": 0.0,
            "weather_code": 0,
            "wind_speed_10m": wind,
        },
        "daily": {
            "time": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05", "2025-01-06", "2025-01-07"],
            "weather_code": [0] * 7,
            "temperature_2m_max": temps,
            "temperature_2m_min": [18] * 7,
            "precipitation_sum": rainfall,
            "precipitation_probability_max": [10] * 7,
        },
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return self.payload


class ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.temp_dir.name) / "legacy.sqlite3"
        with closing(sqlite3.connect(cls.db_path)) as db:
            db.execute(
                """CREATE TABLE farm_profile (
                    id INTEGER PRIMARY KEY,
                    farmer_name TEXT NOT NULL DEFAULT '',
                    location TEXT NOT NULL DEFAULT 'Pune, Maharashtra',
                    farm_size_acres REAL NOT NULL DEFAULT 2,
                    crop TEXT NOT NULL DEFAULT 'Wheat',
                    soil_type TEXT NOT NULL DEFAULT 'Loamy',
                    growth_stage TEXT NOT NULL DEFAULT 'Vegetative'
                )"""
            )
            db.execute(
                """INSERT INTO farm_profile
                   (id, farmer_name, location, farm_size_acres, crop, soil_type, growth_stage)
                   VALUES (1, 'Existing farmer', 'Nashik', 4.5, 'Tomato', 'Black cotton', 'Flowering')"""
            )
            db.execute(
                """CREATE TABLE history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            db.execute(
                "INSERT INTO history (title, details, created_at) VALUES (?, ?, ?)",
                ("Old history", "Keep this record", "2024-01-01T00:00:00+00:00"),
            )
            db.commit()
        cls.database_override = patch.object(main, "DATABASE_PATH", cls.db_path)
        cls.database_override.start()
        cls.client_context = TestClient(main.app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        cls.database_override.stop()
        cls.temp_dir.cleanup()

    def test_additive_migration_preserves_existing_farm_and_history(self):
        farm = self.client.get("/api/farm").json()
        history = self.client.get("/api/history").json()["entries"]
        self.assertEqual(farm["farmer_name"], "Existing farmer")
        self.assertEqual(farm["crop"], "Tomato")
        self.assertTrue(any(entry["title"] == "Old history" for entry in history))
        with closing(sqlite3.connect(self.db_path)) as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(farm_profile)")}
            history_columns = {row[1] for row in db.execute("PRAGMA table_info(history)")}
        self.assertIn("weather_latitude", columns)
        self.assertIn("metadata_json", history_columns)

    def test_weather_location_is_saved_and_restored_after_restart(self):
        location = {"name": "Nagpur, Maharashtra, India", "latitude": 21.1458, "longitude": 79.0882}
        saved = self.client.put("/api/weather/location", json=location)
        self.assertEqual(saved.status_code, 200)
        self.client_context.__exit__(None, None, None)
        self.client_context = TestClient(main.app)
        self.client = self.client_context.__enter__()
        self.assertEqual(self.client.get("/api/weather/location").json(), location)

    def test_farm_crop_and_activity_records_are_persisted_and_counted(self):
        crop = self.client.post(
            "/api/farm/crops",
            json={
                "crop": "Chickpea",
                "variety": "Local",
                "area_acres": 1.25,
                "planting_date": "2025-06-10",
                "growth_stage": "Seedling",
            },
        )
        self.assertEqual(crop.status_code, 201)
        crop_id = crop.json()["id"]
        self.assertEqual(self.client.get("/api/farm/crops").json()["crops"][0]["crop"], "Chickpea")
        update = self.client.put(
            f"/api/farm/crops/{crop_id}",
            json={"crop": "Chickpea", "area_acres": 1.5, "growth_stage": "Vegetative"},
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["area_acres"], 1.5)
        activity = self.client.post(
            "/api/farm/activities",
            json={"activity_type": "irrigation", "details": "Checked soil and irrigated north plot", "crop": "Chickpea"},
        )
        self.assertEqual(activity.status_code, 201)
        self.assertEqual(len(self.client.get("/api/farm/activities").json()["activities"]), 1)
        summary = self.client.get("/api/dashboard/summary").json()
        self.assertEqual(summary["totals"]["activities"], 1)
        self.assertEqual(summary["totals"]["farm_crops"], 1)
        self.assertEqual(len(summary["daily_activity"]), 7)
        self.assertTrue(any(item["count"] for item in summary["daily_activity"]))
        self.assertTrue(self.client.delete(f"/api/farm/crops/{crop_id}").json()["deleted"])
        self.assertEqual(self.client.delete(f"/api/farm/crops/{crop_id}").status_code, 404)

    def test_weather_returns_live_values_risk_and_irrigation_guidance(self):
        payload = weather_payload(rain=[40, 4, 0, 0, 0, 0, 0], high_temps=[40, 31, 30, 31, 32, 33, 34], wind=38)
        with patch.object(main, "urlopen", return_value=FakeResponse(payload)):
            response = self.client.get("/api/weather?latitude=21.1&longitude=79.0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current"]["temperature_2m"], 27.1)
        self.assertEqual(data["source"], "Open-Meteo")
        self.assertEqual(len(data["risks"]), 3)
        self.assertIn("10 mm", data["irrigation_guidance"])

    def test_weather_provider_failure_is_reported(self):
        with patch.object(main, "urlopen", side_effect=URLError("offline")):
            response = self.client.get("/api/weather")
        self.assertEqual(response.status_code, 503)
        self.assertIn("unavailable", response.json()["detail"])

    def test_weather_risk_copy_is_localized(self):
        payload = weather_payload(high_temps=[40, 31, 30, 31, 32, 33, 34])
        with patch.object(main, "urlopen", return_value=FakeResponse(payload)):
            response = self.client.get("/api/weather?language=hi")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["risks"][0]["severity"], "मध्यम")
        self.assertIn("तापमान", response.json()["risks"][0]["title"])
        self.assertIn("साफ आसमान", response.json()["current"]["weather_description"])

    def test_advisory_uses_forecast_context_and_persists_result(self):
        with patch.object(main, "urlopen", return_value=FakeResponse(weather_payload(rain=[8, 6, 0, 0, 0, 0, 0]))):
            response = self.client.post(
                "/api/advisory",
                json={
                    "crop": "Wheat",
                    "soil_type": "Loamy",
                    "location": "Nagpur",
                    "growth_stage": "Flowering",
                    "farm_size_acres": 3.5,
                    "latitude": 21.1,
                    "longitude": 79.0,
                },
            )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result["weather_used"])
        self.assertEqual(result["farm_size_acres"], 3.5)
        self.assertIn("14.0 mm", result["recommendations"][0]["detail"])
        self.assertEqual(len(result["recommendations"]), 5)
        self.assertEqual(self.client.get("/api/history?activity_type=advisory").json()["entries"][0]["crop"], "Wheat")

    def test_advisory_requires_coordinate_pair(self):
        response = self.client.post(
            "/api/advisory",
            json={
                "crop": "Wheat",
                "soil_type": "Loamy",
                "location": "Pune",
                "growth_stage": "Vegetative",
                "latitude": 18.5,
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_advisory_weather_failure_is_reported_in_selected_language(self):
        with patch.object(main, "urlopen", side_effect=URLError("offline")):
            response = self.client.post(
                "/api/advisory",
                json={
                    "crop": "Wheat",
                    "soil_type": "Loamy",
                    "location": "Nagpur",
                    "growth_stage": "Vegetative",
                    "farm_size_acres": 2,
                    "latitude": 21.1,
                    "longitude": 79.0,
                    "language": "hi",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("लाइव मौसम उपलब्ध नहीं था", response.json()["weather_note"])
        self.assertFalse(response.json()["weather_used"])

    def test_assistant_fallback_is_explicit_and_hindi(self):
        with patch.dict(os.environ, {"FARM_ASSISTANT_API_KEY": ""}):
            response = self.client.post(
                "/api/assistant",
                json={"question": "गेहूं में सिंचाई कब करें?", "language": "hi"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "curated_fallback")
        self.assertIn("Curated fallback", response.json()["label"])
        self.assertIn("सिंचाई", response.json()["answer"])

    def test_configured_assistant_calls_provider_without_returning_secret(self):
        provider_response = FakeResponse(
            {"choices": [{"message": {"content": "Check soil moisture first."}}]}
        )
        with patch.dict(
            os.environ,
            {
                "FARM_ASSISTANT_API_KEY": "test-secret",
                "FARM_ASSISTANT_MODEL": "test-model",
            },
        ), patch.object(main, "urlopen", return_value=provider_response) as mocked:
            response = self.client.post(
                "/api/assistant",
                json={"question": "When should I irrigate wheat?", "language": "en"},
            )
            status = self.client.get("/api/assistant/status").json()
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["source"], "configured_provider")
        self.assertIn("test-model", result["label"])
        self.assertNotIn("test-secret", response.text)
        request = mocked.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")
        self.assertTrue(status["generative_available"])

    def test_provider_failure_uses_explicit_curated_fallback(self):
        with patch.dict(os.environ, {"FARM_ASSISTANT_API_KEY": "test-secret"}), patch.object(
            main, "urlopen", side_effect=URLError("provider offline")
        ):
            response = self.client.post(
                "/api/assistant",
                json={"question": "How do I improve soil health?", "language": "en"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "curated_fallback")
        self.assertIn("unavailable", response.json()["label"])
        self.assertIn("soil test", response.json()["answer"])


if __name__ == "__main__":
    unittest.main()
