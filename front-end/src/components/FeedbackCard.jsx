export default function FeedbackCard({ label, value }) {
    return (
        <div className="feedback-card">
            <h3>{label}</h3>
            <p>{value}</p>
        </div>
    )
}