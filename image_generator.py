import json
import time
import requests
import logging
from config import FUSIONBRAIN_URL, FUSIONBRAIN_API_KEY, FUSIONBRAIN_SECRET_KEY

logger = logging.getLogger(__name__)

class FusionBrainAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        """Получает ID pipeline для Kandinsky"""
        try:
            response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
            response.raise_for_status()
            data = response.json()
            for pipeline in data:
                if 'Kandinsky' in pipeline.get('name', ''):
                    return pipeline['id']
            raise ValueError("Не найден pipeline для Kandinsky")
        except Exception as e:
            logger.error(f"Ошибка получения pipeline: {e}")
            raise

    def generate(self, prompt, pipeline_id, images=1, width=512, height=512):
        """Генерирует изображение с negative_prompt"""
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {"query": prompt},
            "negativePromptDecoder": "насилие, запреты, кровь, ужас, нейросети, код, хакинг, технологии, AI, серверы, оружие, политика"
        }
        data = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Задача создана: UUID {data['uuid']}, статус: {data.get('status', 'UNKNOWN')}")
        return data['uuid']

    def check_generation(self, request_id, attempts=40, initial_delay=10):
        """Проверяет статус с экспоненциальным backoff"""
        delay = initial_delay
        while attempts > 0:
            try:
                response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS, timeout=30)
                if response.status_code == 404:
                    logger.error("404: Задача не найдена (возможно, истекла или удалена)")
                    return None
                response.raise_for_status()
                data = response.json()
                logger.info(f"Статус задачи {request_id}: {data.get('status')}")


                
                if data['status'] == 'DONE':
                    if data.get('result', {}).get('censored', False):
                        logger.warning("Генерация заблокирована модерацией")
                        return None
                    return data['result']['files']
                


                elif data['status'] == 'FAIL':
                    logger.error(f"Генерация провалилась: {data.get('errorDescription', 'Unknown error')}")
                    return None
            except requests.exceptions.Timeout:
                logger.warning(f"Таймаут проверки статуса, попытка {attempts}")
            except Exception as e:
                logger.error(f"Ошибка проверки статуса: {e}")
            
            attempts -= 1
            time.sleep(delay)
            delay = min(delay * 1.5, 60)  # Экспоненциальный backoff до 60 сек
        logger.error("Таймаут генерации изображения")
        return None