// TODO: display results of recording
import { useLocation, useNavigate } from 'react-router-dom'
import FeedbackCard from '../components/FeedbackCard'

export default function ResultsPage() {
    const { state } = useLocation()
    const navigate = useNavigate()

    if (!state?.results) {
        navigate('/')
        return null
    }

    // add other tracked data
    const { transcript, filler_word_count, speech_speed, sentence_length, overused_words} = state.results
    
    return (
        <div>
            <h1>Your Results</h1>
            <FeedbackCard label = "Transcript" value = {transcript} />
            <FeedbackCard label = "Filler Words" value = {filler_word_count} />
            <FeedbackCard label="Speaking Pace" value={speech_speed} />
            <FeedbackCard label="Sentence Length" value={sentence_length} />

            <FeedbackCard 
                label = "Overused Words"
                value = {overused_words.map(([word, count]) => `${word} (${count})`).join(', ') || 'None'}
            />
            <button onClick={() => navigate('/')}>Record Again</button>
            <button onClick={() => navigate('/dashboard')}>Go to Dashboard</button>
        </div>
    )
}