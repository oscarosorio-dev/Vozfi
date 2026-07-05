class VozfiError(Exception):
    """Excepción base para errores de dominio de la aplicación."""


class TranscriptionError(VozfiError):
    """Se produce cuando el servicio de transcripción (STT) falla."""


class SynthesisError(VozfiError):
    """Se produce cuando el servicio de síntesis de voz (TTS) falla."""