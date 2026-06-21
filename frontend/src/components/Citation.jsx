function Citation({ citation }) {
    return (
        <article>
            <h3>
                {citation.filename}
            </h3>

            <p>
                Page: {citation.page_number ?? "Not available"}
            </p>

            <p>
                {citation.text}
            </p>
        </article>
    );
}


export default Citation;
