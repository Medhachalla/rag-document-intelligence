import { useState } from "react";

import api from "../api/client";
import getApiErrorMessage from "../api/errors";


function Upload(){
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");
    const [error, setError] = useState("");

    async function upload(event){
        event.preventDefault();

        if (!file) {
            setError("Select a PDF before uploading");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            setIsUploading(true);
            setError("");
            setSuccessMessage("");

            const response = await api.post(
                "/api/v1/documents/upload",
                formData
            );

            setSuccessMessage(`${response.data.filename} uploaded and processing has started.`);
            setFile(null);
            event.currentTarget.reset();
        } catch (requestError) {
            setError(getApiErrorMessage(requestError, "Upload failed"));
        } finally {
            setIsUploading(false);
        }
    }

    function handleFileChange(event) {
        setFile(event.target.files[0] || null);
        setSuccessMessage("");
        setError("");
    }

    return (
        <div>
            <header className="page-header">
                <div>
                    <h1>
                        Upload Document
                    </h1>

                    <p>
                        Add PDFs to the searchable DocSense knowledge base.
                    </p>
                </div>
            </header>

            <form className="upload-panel" onSubmit={upload}>
                <label htmlFor="document-upload">
                    PDF file
                </label>

                <input
                    id="document-upload"
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                />

                {file && (
                    <p className="selected-file">
                        Selected: {file.name}
                    </p>
                )}

                <button type="submit" disabled={isUploading}>
                    {isUploading ? "Uploading..." : "Upload PDF"}
                </button>
            </form>

            {successMessage && (
                <p className="state-message success-message">
                    {successMessage}
                </p>
            )}

            {error && (
                <p className="state-message error-message">
                    {error}
                </p>
            )}
        </div>
    )
}


export default Upload;
