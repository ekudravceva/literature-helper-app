from deep_translator import GoogleTranslator


def translate_text(text: str, source: str = "en", target: str = "ru") -> str:
    if not text or not text.strip():
        return text

    try:
        # Разбиваем длинный текст на части (Google Translate принимает до 5000 символов за раз)
        if len(text) > 5000:
            parts = [text[i:i+5000] for i in range(0, len(text), 5000)]
            translated = GoogleTranslator(source=source, target=target).translate_batch(parts)
            return " ".join(translated)
        else:
            return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text  # Возвращаем оригинал при ошибке