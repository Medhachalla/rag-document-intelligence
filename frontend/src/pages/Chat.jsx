import { useState } from "react";

import api from "../api/client";
import getApiErrorMessage from "../api/errors";
import Citation from "../components/Citation";


function Chat(){
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [citations, setCitations] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    async function submitQuestion(event) {
        event.preventDefault();

        const trimmedQuestion = question.trim();
        if (!trimmedQuestion) {
            setError("Enter a question");
            return;
        }

        try {
            setIsLoading(true);
            setError("");
            setAnswer("");
            setCitations([]);

            const response = await api.post("/v1/query", {
                question: trimmedQuestion,
                top_k: 3,
            });

            setAnswer(response.data.answer);
            setCitations(response.data.citations || []);
        } catch (requestError) {
            setError(getApiErrorMessage(requestError, "Failed to get an answer"));
            setCitations(requestError.response?.data?.citations || []);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="page-stack chat-page">
            <header className="page-header">
                <div>
                    <h1>
                        Ask DocSense
                    </h1>

                    <p>
                        Ask questions and get grounded answers from uploaded PDFs.
                    </p>
                </div>
            </header>

            {error && (
                <p className="state-message error-message">
                    {error}
                </p>
            )}

            <section className="chat-workspace">
                {isLoading && (
                    <p className="state-message">
                        Searching documents and generating an answer...
                    </p>
                )}

                {!isLoading && !answer && !error && (
                    <div className="empty-state compact-empty-state">
                        <h2>
                            Ready to search your documents
                        </h2>

                        <p>
                            Ask a specific question about an uploaded PDF to get a grounded answer with citations.
                        </p>
                    </div>
                )}

                {answer && (
                    <section className="answer-panel">
                        <span className="assistant-label">
                            Answer
                        </span>

                        <p>
                            {answer}
                        </p>
                    </section>
                )}

                {citations.length > 0 && (
                    <section className="citations-section">
                        <h2>
                            Citations
                        </h2>

                        <div className="citation-grid">
                            {citations.map((citation) => (
                                <Citation
                                    key={citation.chunk_id}
                                    citation={citation}
                                />
                            ))}
                        </div>
                    </section>
                )}
            </section>

            <form className="chat-composer" onSubmit={submitQuestion}>
                <label htmlFor="question">
                    Question
                </label>

                <textarea
                    id="question"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ask about a policy, report, manual, or uploaded PDF..."
                    rows="4"
                />

                <div className="composer-actions">
                    <span>
                        Uses top 3 retrieved chunks
                    </span>

                    <button type="submit" disabled={isLoading || !question.trim()}>
                        {isLoading ? "Asking..." : "Ask"}
                    </button>
                </div>
            </form>
        </div>
    )

}


export default Chat;
