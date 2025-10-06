import json
import time
import requests
from config import (
    FUSIONBRAIN_URL,
    FUSIONBRAIN_API_KEY,
    FUSIONBRAIN_SECRET_KEY,
)  # Импорт из твоего config


class FusionBrainAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }

    def check_availability(self):
        response = requests.get(
            self.URL + "key/api/v1/pipeline/availability", headers=self.AUTH_HEADERS
        )
        print(f"Availability: {response.json()}")
        return response.json().get("pipeline_status") != "DISABLED_BY_QUEUE"

    def get_pipeline(self):
        response = requests.get(
            self.URL + "key/api/v1/pipelines", headers=self.AUTH_HEADERS
        )
        data = response.json()
        for p in data:
            if "Kandinsky" in p.get("name", ""):
                return p["id"]
        raise ValueError("No Kandinsky")

    def generate(self, prompt, pipeline_id):
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": 512,
            "height": 512,
            "generateParams": {"query": prompt},
            "negativePromptDecoder": "насилие, запреты, кровь",  # Для безопасности
        }
        data = {
            "pipeline_id": (None, pipeline_id),
            "params": (None, json.dumps(params), "application/json"),
        }
        response = requests.post(
            self.URL + "key/api/v1/pipeline/run", headers=self.AUTH_HEADERS, files=data
        )
        print(f"Generate response: {response.status_code} - {response.json()}")
        return response.json()["uuid"]

    def check_generation(self, uuid, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(
                f"{self.URL}key/api/v1/pipeline/status/{uuid}",
                headers=self.AUTH_HEADERS,
            )
            data = response.json()
            print(f"Status: {data.get('status')} - {data}")
            if data["status"] == "DONE":
                return data["result"]["files"]
            if data["status"] == "FAIL" or response.status_code == 404:
                print("FAIL or 404 - abort")
                return None
            attempts -= 1
            time.sleep(delay)
        return None


if __name__ == "__main__":
    api = FusionBrainAPI(FUSIONBRAIN_URL, FUSIONBRAIN_API_KEY, FUSIONBRAIN_SECRET_KEY)
    if api.check_availability():
        pid = api.get_pipeline()
        uid = api.generate("солнце над морем", pid)
        files = api.check_generation(uid)
        if files:
            print("Success! Base64:", files[0][:50] + "...")
        else:
            print("Failed")
    else:
        print("API unavailable")
