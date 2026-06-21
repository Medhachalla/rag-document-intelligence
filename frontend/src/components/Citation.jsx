function Citation({ citation }) {
    return (
        <article className="citation-card">
            <div className="citation-meta">
                <h3>
                    {citation.filename}
                </h3>

                <span className="page-pill">
                    Page {citation.page_number ?? "N/A"}
                </span>
            </div>

            <span className="citation-label">
                Retrieved text
            </span>

            <p>
                {citation.text}
            </p>
        </article>
    );
}


export default Citation;
