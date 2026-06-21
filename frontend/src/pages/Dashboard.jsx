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

                const response = await api.get("/api/v1/documents");

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
        <div>
            <header className="page-header">
                <div>
                    <h1>
                        Documents
                    </h1>

                    <p>
                        Track uploaded PDFs and processing status.
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
                <div className="document-grid">
                    {documents.map((document) => (
                        <article className="document-card" key={document.id}>
                            <div className="card-header">
                                <h2>
                                    {document.filename}
                                </h2>

                                <StatusBadge status={document.status} />
                            </div>

                            <p className="muted-text">
                                Document ID: {document.id}
                            </p>

                            <p className="meta-row">
                                Uploaded: {formatDate(document.uploaded_at)}
                            </p>

                            {document.status === "failed" && document.error_message && (
                                <div className="error-panel">
                                    <p className="panel-label">
                                        Error:
                                    </p>

                                    <p>
                                        {document.error_message}
                                    </p>
                                </div>
                            )}
                        </article>
                    ))}
                </div>
            )}
        </div>
    )
}


export default Dashboard;
