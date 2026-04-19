const data = JSON.parse(sessionStorage.getItem('results'))

if (!data) {
    window.location.href = '/record'
} else {
    function fillCard(id, label, value) {
        document.getElementById(id).innerHTML = `<h3>${label}</h3><p>${value}</p>`
    }

    fillCard('transcript-card', 'Transcript', data.transcript)
    fillCard('filler-card', 'Filler Words', data.filler_word_count)
    fillCard('pace-card', 'Speaking Pace', data.speech_speed)
    fillCard('sentence-card', 'Sentence Length', data.sentence_length)
    fillCard('overused-card', 'Overused Words',
        data.overused_words?.map(([w, n]) => `"${w}" (${n}x)`).join(', ') || 'None'
    )
}
