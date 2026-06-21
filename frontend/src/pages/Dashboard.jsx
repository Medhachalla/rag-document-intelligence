import { useEffect, useState } from "react";

import api from "../api/client";


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


function formatStatus(status) {
    if (status === "ready") {
        return "completed";
    }

    return status || "unknown";
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
            } catch {
                if (isMounted) {
                    setError("Failed to load documents");
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
            <h1>
                Documents
            </h1>

            {isLoading && (
                <p>
                    Loading documents...
                </p>
            )}

            {!isLoading && error && (
                <p>
                    {error}
                </p>
            )}

            {!isLoading && !error && documents.length === 0 && (
                <p>
                    No documents uploaded yet
                </p>
            )}

            {!isLoading && !error && documents.length > 0 && (
                <div>
                    {documents.map((document) => (
                        <article key={document.id}>
                            <h2>
                                {document.filename}
                            </h2>

                            <p>
                                Document ID: {document.id}
                            </p>

                            <p>
                                Status: {formatStatus(document.status)}
                            </p>

                            <p>
                                Uploaded: {formatDate(document.uploaded_at)}
                            </p>

                            {document.status === "failed" && document.error_message && (
                                <div>
                                    <p>
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
