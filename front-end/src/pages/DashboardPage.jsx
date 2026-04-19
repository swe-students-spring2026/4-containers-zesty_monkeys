import { useEffect, useState } from 'react'

export default function DashboardPage() {
    const [records, setRecords] = useState([])
    const [loading, setLoading] = useState(true)


    useEffect(() => {
        //TOD: replace with real fetch from backend

        setRecords([
            { 
                id: 1, 
                transcript: "We are, um, two white colored foreigners, um, riding motorcyles together, like, to cross China.",
                speech_speed: "Average",
                filler_word_count: 3,
                sentence_length: "Long",
                overused_words: [["um", 2], ["like", 1]]
            },

            { 
                id: 2, 
                transcript: "We are, um, two white colored foreigners, um, riding motorcyles together, like, to cross China.",
                speech_speed: "Fast",
                filler_word_count: 3,
                sentence_length: "Long",
                overused_words: [["um", 2], ["like", 1]]
            }
        ])
        setLoading(false)
    }, [])

    if (loading) return <div>Loading...</div>

    return (
        <div>
            <h1>Dashboard</h1>
            {records.length === 0
                ? <p>No past recordings.</p>
                : records.map( r => (
                    <div key={r.id}>
                        <p>{r.transcript}</p>
                        <p>Pace: {r.speech_speed}</p>
                        <p>Filler Words: {r.filler_word_count}</p>
                        <p>Sentence Length: {r.sentence_length}</p>
                        <p>Overused Words: {r.overused_words.map(([w, n]) => `${w} (${n})`).join(', ') || 'None'}</p>
                    </div>
                ))
            }
        </div>
    )
}