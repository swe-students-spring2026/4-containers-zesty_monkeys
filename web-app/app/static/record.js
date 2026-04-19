let mediaRecorder
let chunks = []
let audioBlob = null

const recordBtn = document.getElementById('record-btn')
const submitBtn = document.getElementById('submit-btn')
const fileInput = document.getElementById('file-input')
const audioStatus = document.getElementById('audio-status')
const errorMsg = document.getElementById('error-msg')

recordBtn.addEventListener('click', async () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop()
        recordBtn.textContent = 'Start Recording'
    } else {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder = new MediaRecorder(stream)
        chunks = []

        mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(chunks, { type: 'audio/webm' })
            audioStatus.textContent = 'Audio ready.'
            submitBtn.disabled = false
        }

        mediaRecorder.start()
        recordBtn.textContent = 'Stop Recording'
    }
})

fileInput.addEventListener('change', () => {
    audioBlob = fileInput.files[0]
    audioStatus.textContent = 'Audio ready.'
    submitBtn.disabled = false
})

submitBtn.addEventListener('click', async () => {
    if (!audioBlob) return
    submitBtn.disabled = true
    submitBtn.textContent = 'Analyzing...'

    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData })
        const data = await res.json()
        // store results and go to results page
        sessionStorage.setItem('results', JSON.stringify(data))
        window.location.href = '/results'
    } catch (err) {
        errorMsg.textContent = 'Something went wrong. Please try again.'
        submitBtn.disabled = false
        submitBtn.textContent = 'Analyze'
    }
})
