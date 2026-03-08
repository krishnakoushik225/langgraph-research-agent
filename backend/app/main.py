from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.api import ResearchRequest, ResearchResponse
from app.graph.builder import build_research_graph

app = FastAPI(title="ResearchFlow AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

research_graph = build_research_graph()


@app.get("/")
def root():
    return {"message": "ResearchFlow AI backend is running"}


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    try:
        result = research_graph.invoke({
            "question": request.question,
            "iteration_count": 0
        })

        return ResearchResponse(
            question=result.get("question", request.question),
            plan=result.get("plan", ""),
            sub_questions=result.get("sub_questions", []),
            search_results=result.get("search_results", []),
            verification_notes=result.get("verification_notes", ""),
            confidence_score=result.get("confidence_score", 0.0),
            reflection_notes=result.get("reflection_notes", ""),
            final_answer=result.get("final_answer", ""),
            citations=result.get("citations", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))