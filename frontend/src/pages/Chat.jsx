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

            const response = await api.post("/api/v1/query", {
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
        <div>
            <header className="page-header">
                <div>
                    <h1>
                        Chat
                    </h1>

                    <p>
                        Ask questions and get grounded answers from uploaded PDFs.
                    </p>
                </div>
            </header>

            <form className="chat-form" onSubmit={submitQuestion}>
                <label htmlFor="question">
                    Question
                </label>

                <textarea
                    id="question"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ask a question about your uploaded documents"
                    rows="4"
                />

                <button type="submit" disabled={isLoading || !question.trim()}>
                    {isLoading ? "Asking..." : "Ask"}
                </button>
            </form>

            {isLoading && (
                <p className="state-message">
                    Searching documents and generating an answer...
                </p>
            )}

            {error && (
                <p className="state-message error-message">
                    {error}
                </p>
            )}

            {answer && (
                <section className="answer-panel">
                    <h2>
                        Answer
                    </h2>

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
        </div>
    )

}


export default Chat;
