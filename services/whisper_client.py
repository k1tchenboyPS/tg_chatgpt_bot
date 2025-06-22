import whisper
import logging
import asyncio

logger = logging.getLogger(__name__)

model = whisper.load_model("base")

async def transcribe_audio(path):
    try:
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            None,
            lambda: model.transcribe(path, language="russian")
        )

        text = result.get("text", "").strip()
        logger.info(f"📄 Whisper результат: {text}")

        return text if text else "Речь не распознана."

    except Exception as e:
        logger.error(f"❌ Ошибка в transcribe_audio: {e}")
        return "Ошибка распознавания аудио."