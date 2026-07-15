# Vozfi — Mobile

Cliente Expo (React Native) de Vozfi — es el cliente principal del proyecto. Ver el [README raíz](../README.md) para la arquitectura completa.

## Pantallas

- **Inicio** — micrófono como acción principal (`expo-audio` para grabar), balance compacto del período. Al soltar, el audio se envía a `/voice/voice-input` y se reproduce la respuesta hablada del agente.
- **Registros** — lista de transacciones con búsqueda, filtro por tipo, swipe-to-delete, edición y creación manual (fallback para cuando la voz no es viable).
- **Resumen** — balance detallado, gráfico mensual (ingresos vs. gastos) y desglose por categoría.
- **`/record`** — pantalla de captura rápida que inicia grabación automáticamente al abrirse; pensada como destino de deep links (`vozfi://record`) y, a futuro, de App Shortcuts / Siri.

## Stack

Expo SDK 54, Expo Router (file-based), TypeScript, TanStack Query (cache/fetch del backend), `expo-audio` + `expo-file-system` (grabación y reproducción de voz), `react-native-gifted-charts` (gráficos).

## Correr

```bash
cp env.example .env
# editar EXPO_PUBLIC_API_URL según tu entorno (ver tabla abajo)
yarn install
yarn start
```

| Entorno | `EXPO_PUBLIC_API_URL` |
|---|---|
| Simulador iOS | `http://localhost:8000` |
| Emulador Android | `http://10.0.2.2:8000` |
| Dispositivo físico (Expo Go) | IP local de tu máquina, ej: `http://192.168.1.X:8000` |

## Notas técnicas

- **Grabación de audio**: `RecordingPresets.HIGH_QUALITY` produce `.m4a`; se envía como `audio/mp4`, aceptado por Groq y validado contra la whitelist de content-types del backend.
- **Reproducción del TTS**: la respuesta llega en base64 (`audio_base64`); se escribe a un archivo temporal con `expo-file-system` (API basada en clases `File`/`Paths` de SDK 54) antes de reproducirse, porque los players nativos no soportan `data:` URIs de forma confiable.
- **Expo Go vs Dev Client**: todo lo actual corre en Expo Go. Funcionalidades futuras como App Shortcuts / widgets de home screen (`expo-quick-actions`) requieren migrar a un Dev Client (`npx expo prebuild`), ya que dependen de config plugins nativos que Expo Go no incluye.

## Estructura

```
app/              # rutas (Expo Router)
  (tabs)/         # Inicio, Registros, Resumen
  transaction/    # detalle/editar, crear manual
  record.tsx      # captura rápida (deep link)
components/
  voice/          # MicButton, VoiceStatusIndicator, ConversationFeedback
  finance/        # BalanceCard, TransactionRow, MonthlyChart, CategoryBreakdown
hooks/            # useVoicePipeline, useVoiceRecorder, hooks de TanStack Query
lib/              # cliente API tipado
```