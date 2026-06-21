import { useState } from "react";

import api from "../api/client";
import getApiErrorMessage from "../api/errors";


function Upload(){
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
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

    function handleDragOver(event) {
        event.preventDefault();
        setIsDragging(true);
    }

    function handleDragLeave() {
        setIsDragging(false);
    }

    function handleDrop(event) {
        event.preventDefault();
        setIsDragging(false);
        setSuccessMessage("");
        setError("");

        const droppedFile = event.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
        }
    }

    return (
        <div className="page-stack narrow-page">
            <header className="page-header">
                <div>
                    <h1>
                        Upload document
                    </h1>

                    <p>
                        Add a PDF to the searchable knowledge base. Processing starts immediately after upload.
                    </p>
                </div>
            </header>

            <form className="upload-panel" onSubmit={upload}>
                <label
                    className={`upload-dropzone ${isDragging ? "is-dragging" : ""}`}
                    htmlFor="document-upload"
                    onDragLeave={handleDragLeave}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                >
                    <span className="dropzone-title">
                        Drop a PDF here, or browse
                    </span>

                    <span className="dropzone-description">
                        PDF files only. The backend will extract, chunk, embed, and index the document.
                    </span>

                    <input
                        id="document-upload"
                        type="file"
                        accept=".pdf,application/pdf"
                        onChange={handleFileChange}
                    />
                </label>

                {file && (
                    <div className="selected-file">
                        <span>
                            Selected file
                        </span>

                        <strong>
                            {file.name}
                        </strong>
                    </div>
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
