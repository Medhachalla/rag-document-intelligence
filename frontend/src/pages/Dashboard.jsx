import { useEffect, useState } from "react";

import api from "../api/client";
import getApiErrorMessage from "../api/errors";
import StatusBadge from "../components/StatusBadge";


function formatDate(value) {
    if (!value) {
        return "Not available";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function Dashboard(){
    const [documents, setDocuments] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let isMounted = true;

        async function loadDocuments() {
            try {
                setIsLoading(true);
                setError("");

                const response = await api.get("/v1/documents");

                if (isMounted) {
                    setDocuments(response.data);
                }
            } catch (requestError) {
                if (isMounted) {
                    setError(getApiErrorMessage(requestError, "Failed to load documents"));
                }
            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        }

        loadDocuments();

        return () => {
            isMounted = false;
        };
    }, []);

    return (
        <div className="page-stack">
            <header className="page-header">
                <div>
                    <h1>
                        Document dashboard
                    </h1>

                    <p>
                        Monitor uploaded PDFs, ingestion status, and processing issues.
                    </p>
                </div>
            </header>

            {isLoading && (
                <p className="state-message">
                    Loading documents...
                </p>
            )}

            {!isLoading && error && (
                <p className="state-message error-message">
                    {error}
                </p>
            )}

            {!isLoading && !error && documents.length === 0 && (
                <section className="empty-state">
                    <h2>
                        No documents uploaded yet
                    </h2>

                    <p>
                        Upload a PDF to start building your document knowledge base.
                    </p>
                </section>
            )}

            {!isLoading && !error && documents.length > 0 && (
                <section className="document-list" aria-label="Uploaded documents">
                    <div className="document-list-header">
                        <span>
                            Document
                        </span>

                        <span>
                            Status
                        </span>

                        <span>
                            Uploaded
                        </span>
                    </div>

                    <div className="document-list-body">
                        {documents.map((document) => (
                            <article className="document-row" key={document.id}>
                                <div className="document-main">
                                    <h2>
                                        {document.filename}
                                    </h2>

                                    <p>
                                        ID {document.id}
                                    </p>
                                </div>

                                <div className="document-status">
                                    <StatusBadge status={document.status} />
                                </div>

                                <p className="document-date">
                                    {formatDate(document.uploaded_at)}
                                </p>

                                {document.status === "failed" && document.error_message && (
                                    <div className="error-panel document-error">
                                        <p className="panel-label">
                                            Processing error
                                        </p>

                                        <p>
                                            {document.error_message}
                                        </p>
                                    </div>
                                )}
                            </article>
                        ))}
                    </div>
                </section>
            )}
        </div>
    )
}


export default Dashboard;
