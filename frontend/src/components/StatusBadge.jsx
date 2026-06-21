function getStatusLabel(status) {
    if (status === "ready") {
        return "completed";
    }

    return status || "unknown";
}


function StatusBadge({ status }) {
    const label = getStatusLabel(status);

    return (
        <span className={`status-badge status-${label}`}>
            {label}
        </span>
    );
}


export default StatusBadge;
