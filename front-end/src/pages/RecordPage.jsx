import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

export default function RecordPage() {
    const [recording, setRecording] = useState(false)
    const [audioBlob, setAudioBlob] = useState(null)
    const [loading, setLoading] = useState(false)
    const mediaRecorderRef = useRef(null)
    const chunksRef = useRef([])
    const navigate = useNavigate()

    async function startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

        const mediaRecorder = new MediaRecorder(stream)
        mediaRecorderRef.current = mediaRecorder
        chunksRef.current = []

        mediaRecorder.ondataavailable = (e) => chunksRef.current.push(e.data)
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
            setAudioBlob(blob)

        }

        mediaRecorder.start()
        setRecording(true)
    }

    function stopRecording() {
        mediaRecorderRef.current.stop()
        setRecording(false)
    }

    function handleFileUpload(e) {
        setAudioBlob(e.target.files[0])
    }

    async function handleSubmit() {
        if (!audioBlob) return
        setLoading(true)

        const formData = new FormData()
        formData.append('audio', audioBlob, 'recording.webm')

        // mock data, to be replaced
        const data = {
            transcript: "Hi, um, this is zesty monkeys, and we're doing a web app, that's like, um, Uber but for dogs or something.",
            filler_word_count: 4,
            speech_speed: "Average",
            sentence_length: "Long",
            overused_words: [["um", 2], ["like", 1], ["or something", 1]]
        }

        setLoading(false)
        navigate('/results', { state: {results: data} })
    }

    return (
        <div>
      <h1>Speech Analyzer</h1>
      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? 'Stop Recording' : 'Start Recording'}
      </button>
      <p>— or —</p>
      <input type="file" accept="audio/*" onChange={handleFileUpload} />
      {audioBlob && <p>Audio ready.</p>}
      <button onClick={handleSubmit} disabled={!audioBlob || loading}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </div>
    )
}