from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import re
import os
from contextlib import asynccontextmanager
from evaluate import load_ground_truth, evaluate_model 

df = None
tfidf_matrix = None
vectorizer = None

TEST_TYPE_MAPPING = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

def load_and_preprocess_data():
    global df, tfidf_matrix, vectorizer
    print("🔄 Initializing resources...")

    df = pd.read_csv("product_catalog.csv")
    df.dropna(subset=["description"], inplace=True)
    df.fillna("", inplace=True)
    corpus = df["description"] + " " + df["test_type"] + " " + df["url"] + " " + df.get("name", "")
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)

    print("✅ Resources initialized successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_and_preprocess_data()
    yield

app = FastAPI(title="SHL Assessment Recommender API", lifespan=lifespan)

class QueryRequest(BaseModel):
    query: str

class AssessmentResponse(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

def clean_query(query: str) -> str:
    query = query.strip()
    query = re.sub(r'\s+', ' ', query)
    return query

def recommend_func(query: str) -> List[Dict]:
    query = clean_query(query)
    if not query:
        return []

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1][:10]

    recommendations = []
    for idx in top_indices:
        if similarities[idx] == 0:
            continue
        item = df.iloc[idx]
        test_type_codes = [t.strip() for t in str(item["test_type"]).split(",") if t.strip()]
        test_type_full = [TEST_TYPE_MAPPING.get(code, code) for code in test_type_codes]

        recommendations.append({
            "url": item["url"],
            "name": item.get("name", ""),
            "adaptive_support": item["adaptive_support"],
            "description": item["description"],
            "duration": int(item["duration"]),
            "remote_support": item["remote_support"],
            "test_type": test_type_full
        })

    return recommendations


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy"}

@app.post("/recommend", response_model=Dict[str, List[AssessmentResponse]])
async def recommend_assessments(request: QueryRequest):
    """Return top 10 recommended assessments based on user query."""
    query = clean_query(request.query)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    try:
        recommended = recommend_func(query)
        if not recommended:
            return {
                "recommended assessments": [{
                    "url": "",
                    "name": "",
                    "adaptive_support": "No",
                    "description": "No relevant assessment found.",
                    "duration": 0,
                    "remote_support": "No",
                    "test_type": []
                }]
            }

        return {"recommended assessments": recommended}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing recommendation: {str(e)}"
        )

@app.get("/evaluate")
def evaluate_endpoint():
    """
    Evaluate recommendation performance using Recall@10
    and produce a CSV with Query–Assessment_url pairs.
    """
    try:
        ground_truth = load_ground_truth("GEN_AI Dataset.xlsx")
        mean_recall, recall_details = evaluate_model(ground_truth, recommend_func)

        return {
            "message": "Evaluation completed successfully",
            "mean_recall_at_10": round(mean_recall, 3),
            "query_wise_recall": recall_details,
            "output_file": "recommendation_results.csv"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
