import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def load_ground_truth(file_path="GEN_AI Dataset.xlsx"):
    df = pd.read_excel(file_path)
    df = df.dropna(subset=["Query", "Assessment_url"])
    ground_truth = {}

    for _, row in df.iterrows():
        q = row["Query"].strip()
        url = row["Assessment_url"].strip()
        ground_truth.setdefault(q, []).append(url)
    return ground_truth

def evaluate_model(ground_truth, recommend_func):
    results = []
    recalls = []
    recall_details = {}

    for query, true_urls in ground_truth.items():
        predictions = recommend_func(query)
        predicted_urls = [p["url"] for p in predictions]

        relevant_found = sum(url in predicted_urls[:10] for url in true_urls)
        recall = relevant_found / len(true_urls) if len(true_urls) > 0 else 0
        recalls.append(recall)
        recall_details[query] = round(recall, 3)

        for url in predicted_urls[:10]:
            results.append({"Query": query, "Assessment_url": url})

    output_df = pd.DataFrame(results)
    output_df.to_csv("recommendation_results.csv", index=False)

    mean_recall = sum(recalls) / len(recalls) if recalls else 0
    return mean_recall, recall_details
