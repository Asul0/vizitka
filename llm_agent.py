from langchain_gigachat import GigaChat
from langchain_core.messages import SystemMessage, HumanMessage
import logging
import asyncio

from config import (
    GIGACHAT_CREDENTIALS,
    GIGACHAT_SCOPE,
    GIGACHAT_VERIFY_SSL_CERTS,
    GIGACHAT_MODEL,
    GIGACHAT_TIMEOUT,
    GIGACHAT_PROFANITY_CHECK,
    GIGACHAT_TEMPERATURE,
    GIGACHAT_MAX_TOKENS,
)

logger = logging.getLogger(__name__)


class GigaChatManagerAssistant:
    def __init__(self):
        self.client = GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            scope=GIGACHAT_SCOPE,
            verify_ssl_certs=GIGACHAT_VERIFY_SSL_CERTS,
            model=GIGACHAT_MODEL,
            timeout=GIGACHAT_TIMEOUT,
            profanity_check=GIGACHAT_PROFANITY_CHECK,
            temperature=GIGACHAT_TEMPERATURE,
            max_tokens=GIGACHAT_MAX_TOKENS,
        )

    def get_analysis(self, system_prompt: str, user_prompt: str) -> str:
        return self._invoke_llm_with_retry(system_prompt, user_prompt)

    def _invoke_llm_with_retry(
        self, system_prompt: str, user_prompt: str, max_retries: int = 3
    ) -> str:
        """Вызов LLM с retry на таймаут"""
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Отправляем запрос к GigaChat (попытка {attempt + 1}/{max_retries})"
                )
                response = self.client.invoke(
                    [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt),
                    ]
                )
                logger.info("Получен ответ от GigaChat")
                return response.content.strip()
            except Exception as e:
                logger.error(f"Ошибка GigaChat (попытка {attempt + 1}): {e}")
                if "timed out" in str(e).lower() and attempt < max_retries - 1:
                    logger.info("Таймаут, ждём 5 сек и повторяем...")
                    asyncio.sleep(5)
                else:
                    return f"Ошибка при обращении к ИИ (после {max_retries} попыток): {str(e)}"
        return "Ошибка: Не удалось получить ответ от ИИ после нескольких попыток."
