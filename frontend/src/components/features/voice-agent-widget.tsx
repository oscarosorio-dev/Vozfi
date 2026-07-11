"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { sendVoiceAgent } from "@/lib/api"
import { Mic, Square, Loader2, Volume2 } from "lucide-react"

export function VoiceAgentWidget({ onActionCompleted }: { onActionCompleted: () => void }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [response, setResponse] = useState("")
  const [isPlaying, setIsPlaying] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" })
        await handleAudioUpload(audioBlob)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error(error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleAudioUpload = async (blob: Blob) => {
    setIsProcessing(true)
    try {
      const result = await sendVoiceAgent(blob)
      setTranscript(result.transcript)
      setResponse(result.answer_text)
      if (result.audio_base64 && result.audio_content_type) {
        playAudio(result.audio_base64, result.audio_content_type)
      }
      onActionCompleted()
    } catch (error) {
      console.error(error)
    } finally {
      setIsProcessing(false)
    }
  }

  const playAudio = (base64: string, contentType: string) => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause()
    }
    const audioSrc = `data:${contentType};base64,${base64}`
    const audio = new Audio(audioSrc)
    audioPlayerRef.current = audio
    audio.onplay = () => setIsPlaying(true)
    audio.onended = () => setIsPlaying(false)
    audio.play().catch((err) => console.error(err))
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Asistente de Voz Inteligente</CardTitle>
        <CardDescription>Presiona para hablar con el agente y gestionar tus finanzas en lenguaje natural.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center space-y-6">
        <div className="flex justify-center">
          {!isRecording ? (
            <Button
              onClick={startRecording}
              disabled={isProcessing}
              variant="default"
              className="h-20 w-20 rounded-full flex items-center justify-center transition-all shadow-md bg-zinc-900 hover:bg-zinc-800 text-white"
            >
              <Mic className="h-8 w-8" />
            </Button>
          ) : (
            <Button
              onClick={stopRecording}
              variant="destructive"
              className="h-20 w-20 rounded-full flex items-center justify-center animate-pulse transition-all shadow-md"
            >
              <Square className="h-8 w-8" />
            </Button>
          )}
        </div>

        {isProcessing && (
          <div className="flex items-center space-x-2 text-zinc-600 dark:text-zinc-400">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Procesando y consultando herramientas...</span>
          </div>
        )}

        {isPlaying && (
          <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
            <Volume2 className="h-5 w-5 animate-bounce" />
            <span className="text-sm font-medium">Sintetizando y reproduciendo audio de respuesta...</span>
          </div>
        )}

        {(transcript || response) && (
          <div className="w-full space-y-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            {transcript && (
              <div className="space-y-1">
                <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Tu voz transcrita</p>
                <p className="text-sm text-zinc-800 dark:text-zinc-200 bg-zinc-50 dark:bg-zinc-900 p-3 rounded-lg border border-zinc-100 dark:border-zinc-800">
                  &quot;{transcript}&quot;
                </p>
              </div>
            )}
            {response && (
              <div className="space-y-1">
                <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Respuesta del agente</p>
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50 bg-zinc-50 dark:bg-zinc-900 p-3 rounded-lg border border-zinc-100 dark:border-zinc-800">
                  {response}
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}