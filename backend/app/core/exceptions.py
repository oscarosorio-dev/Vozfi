class VozfiError(Exception):
    """Excepción base para errores de dominio de la aplicación."""


class TranscriptionError(VozfiError):
    """Se produce cuando el servicio de transcripción (STT) falla."""


class SynthesisError(VozfiError):
    """Se produce cuando el servicio de síntesis de voz (TTS) falla."""


class ParsingError(VozfiError):
    """Se produce cuando el LLM no logra extraer una transacción válida del texto."""


class QueryAnsweringError(VozfiError):
    """Se produce cuando el LLM no logra generar una respuesta a una consulta financiera."""