import { useState } from "react";

import api from "../api/client";
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
            });

            setAnswer(response.data.answer);
            setCitations(response.data.citations || []);
        } catch (requestError) {
            const message = requestError.response?.data?.message || "Failed to get an answer";

            setError(message);
            setCitations(requestError.response?.data?.citations || []);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div>
            <h1>
                Chat
            </h1>

            <form onSubmit={submitQuestion}>
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

                <button type="submit" disabled={isLoading}>
                    {isLoading ? "Asking..." : "Ask"}
                </button>
            </form>

            {error && (
                <p>
                    {error}
                </p>
            )}

            {answer && (
                <section>
                    <h2>
                        Answer
                    </h2>

                    <p>
                        {answer}
                    </p>
                </section>
            )}

            {citations.length > 0 && (
                <section>
                    <h2>
                        Citations
                    </h2>

                    {citations.map((citation) => (
                        <Citation
                            key={citation.chunk_id}
                            citation={citation}
                        />
                    ))}
                </section>
            )}
        </div>
    )

}


export default Chat;
