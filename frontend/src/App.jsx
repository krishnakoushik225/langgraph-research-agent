import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const SAMPLE_QUESTIONS = [
  "How do reflection agents reduce hallucinations?",
  "What are LangGraph checkpoints used for?",
  "How does conditional routing work in LangGraph?",
];

const isLikelyAIDomainQuestion = (text) => {
  const q = text.toLowerCase();
  const keywords = [
    "langgraph",
    "langchain",
    "agent",
    "agents",
    "reflection",
    "retry",
    "checkpoint",
    "checkpoints",
    "routing",
    "workflow",
    "workflows",
    "rag",
    "llm",
    "llms",
    "ai",
    "prompt",
    "prompts",
    "hallucination",
    "state",
  ];

  return keywords.some((keyword) => q.includes(keyword));
};

function App() {
  const [question, setQuestion] = useState(
    "How does LangGraph enable self-correcting AI agents?"
  );
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState("");
  const [showSources, setShowSources] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const animateLoadingSteps = () => {
    const steps = [
      "Planning research...",
      "Generating sub-questions...",
      "Searching sources...",
      "Verifying evidence...",
      "Synthesizing answer...",
    ];

    let index = 0;
    setLoadingStep(steps[0]);

    const interval = setInterval(() => {
      index = (index + 1) % steps.length;
      setLoadingStep(steps[index]);
    }, 1200);

    return interval;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setShowSources(false);
    setShowSearchResults(false);

    const interval = animateLoadingSteps();

    try {
      const response = await axios.post(`${API_BASE}/research`, {
        question,
      });
      setResult(response.data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Something went wrong while calling the backend."
      );
    } finally {
      clearInterval(interval);
      setLoading(false);
      setLoadingStep("");
    }
  };

  return (
    <div className="app-shell">
      <div className="container">
        <header className="hero">
          <h1>ResearchFlow AI</h1>
          <p>
            A self-correcting agentic research pipeline built with LangGraph,
            Tavily, Ollama, and FastAPI.
          </p>
        </header>

        <section className="card">
          <form onSubmit={handleSubmit} className="question-form">
          <label htmlFor="question" className="label">
            Research Question
          </label>

          <div className="domain-banner">
            <span className="domain-badge">Domain: AI / LangGraph Research</span>
            <p className="domain-text">
                Best for questions about LangGraph, agent workflows, reflection loops,
                checkpoints, conditional routing, and related AI system design topics.
            </p>

            {question.trim() && !isLikelyAIDomainQuestion(question) && (
            <p className="domain-warning">
            This question may be outside the app’s research domain. Results are best
            for AI and LangGraph-related topics.
        </p>
        )}
    </div>

   <textarea
    id="question"
    value={question}
    onChange={(e) => setQuestion(e.target.value)}
    placeholder="Type your research question here..."
    rows={5}
    />

            <div className="sample-questions">
              <span className="sample-label">Try an example:</span>
              {SAMPLE_QUESTIONS.map((sample, index) => (
                <button
                  key={index}
                  type="button"
                  className="sample-button"
                  onClick={() => setQuestion(sample)}
                >
                  {sample}
                </button>
              ))}
            </div>

            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? "Running research..." : "Run Research"}
            </button>

            {loadingStep && <p className="loading-step">{loadingStep}</p>}
          </form>
        </section>

        {error && (
          <section className="card error-card">
            <h2>Error</h2>
            <p>{error}</p>
          </section>
        )}

        {result && (
          <div className="results-grid">
            <section className="card">
              <h2>Plan</h2>
              <p>{result.plan || "No plan returned."}</p>
            </section>

            <section className="card">
              <h2>Confidence</h2>
              <div className="confidence-row">
                <span className="confidence-score">
                  {typeof result.confidence_score === "number"
                    ? result.confidence_score.toFixed(2)
                    : "N/A"}
                </span>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${
                        typeof result.confidence_score === "number"
                          ? Math.max(0, Math.min(100, result.confidence_score * 100))
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>
              <p className="muted">
                {result.verification_notes || "No verification notes returned."}
              </p>
              {result.reflection_notes && result.confidence_score < 0.75 && (
                <div className="reflection-box">
                  <strong>Reflection notes:</strong>
                  <p>{result.reflection_notes}</p>
                </div>
              )}
            </section>
            
            <section className="card full-width">
                <h2>Research Trace</h2>
                <div className="trace-grid">
                  <div className="trace-step">
                    <span className="trace-badge">1</span>
                      <div>
                        <h3>Question</h3>
                        <p>{result.question}</p>
                      </div>
                  </div>

    <div className="trace-step">
      <span className="trace-badge">2</span>
      <div>
        <h3>Plan</h3>
        <p>{result.plan || "No plan returned."}</p>
      </div>
    </div>

    <div className="trace-step">
      <span className="trace-badge">3</span>
      <div>
        <h3>Sub-questions</h3>
        <ul className="clean-list">
          {(result.sub_questions || []).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
    </div>

    <div className="trace-step">
      <span className="trace-badge">4</span>
      <div>
        <h3>Verification</h3>
        <p>
          Confidence score:{" "}
          {typeof result.confidence_score === "number"
            ? result.confidence_score.toFixed(2)
            : "N/A"}
        </p>
        <p className="muted">
          {result.verification_notes || "No verification notes returned."}
        </p>
      </div>
    </div>

    <div className="trace-step">
      <span className="trace-badge">5</span>
      <div>
        <h3>Reflection / Retry</h3>
        <p>
          {result.reflection_notes
            ? result.reflection_notes
            : "No retry was needed."}
        </p>
      </div>
    </div>

    <div className="trace-step">
      <span className="trace-badge">6</span>
      <div>
        <h3>Synthesis</h3>
        <p>Final source-grounded answer generated from retrieved evidence.</p>
      </div>
    </div>
  </div>
</section>

            <section className="card full-width">
              <h2>Final Answer</h2>
              <div className="answer-box">
              {(result.final_answer || "No answer returned.")
                .split("\n")
                .map((line, index) => {

              if (line.startsWith("- ")) {
                  return (
                  <li key={index} className="answer-bullet">
                  {line.replace("- ", "")}
                  </li>
                  );
                }

    if (line.startsWith("Limitation")) {
      return (
        <p key={index} className="answer-limitation">
          {line}
        </p>
      );
    }

    return (
      <p key={index} className="answer-line">
        {line}
      </p>
    );
  })}
              </div>
            </section>

            <section className="card full-width collapsible-card">
              <button
                type="button"
                className="collapse-toggle"
                onClick={() => setShowSources((prev) => !prev)}
              >
                Sources {showSources ? "▲" : "▼"}
              </button>

              {showSources && (
                <div className="sources-list">
                  {(result.citations || []).map((citation) => (
                    <div key={citation.id} className="source-item">
                      <div className="source-top">
                        <span className="badge">[{citation.id}]</span>
                        <a
                          href={citation.url}
                          target="_blank"
                          rel="noreferrer"
                          className="source-link"
                        >
                          {citation.title}
                        </a>
                      </div>
                      <p className="muted">{citation.sub_question}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="card full-width collapsible-card">
              <button
                type="button"
                className="collapse-toggle"
                onClick={() => setShowSearchResults((prev) => !prev)}
              >
                Search Results {showSearchResults ? "▲" : "▼"}
              </button>

              {showSearchResults && (
                <div className="search-results">
                  {(result.search_results || []).map((item, index) => (
                    <div key={index} className="search-item">
                      <div className="search-meta">
                        <span className="badge">{item.status || "unknown"}</span>
                        <span className="muted">
                          Score: {item.score ?? "N/A"}
                        </span>
                      </div>
                      <h3>{item.title}</h3>
                      <p className="muted">
                        <strong>Sub-question:</strong> {item.sub_question}
                      </p>
                      {item.url && (
                        <a href={item.url} target="_blank" rel="noreferrer">
                          {item.url}
                        </a>
                      )}
                      <p>{item.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
        <footer className="footer">
          <p>
            Built with LangGraph, Tavily Search, Ollama (local LLM), FastAPI, and React.
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;