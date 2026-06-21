function Citation({ citation }) {
    return (
        <article className="citation-card">
            <div className="card-header">
                <h3>
                    {citation.filename}
                </h3>

                <span className="page-pill">
                    Page {citation.page_number ?? "N/A"}
                </span>
            </div>

            <p>
                {citation.text}
            </p>
        </article>
    );
}


export default Citation;
