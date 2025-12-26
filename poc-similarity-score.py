from sentence_transformers import SentenceTransformer, util

# Load a fast, lightweight embedding model
MODEL = r"D:\ai\hugging-face\model\all-MiniLM-L6-v2"
evaluator_model = SentenceTransformer(MODEL)


def get_similarity(prediction, ground_truth):
    # Convert text to vectors
    emb1 = evaluator_model.encode(prediction, convert_to_tensor=True)
    emb2 = evaluator_model.encode(ground_truth, convert_to_tensor=True)

    # Compute cosine similarity (returns a value between 0 and 1)
    cosine_score = util.cos_sim(emb1, emb2)
    return cosine_score.item()


# Example test
model_out = "BMI stands for Body Mass Index."
expected = "The acronym BMI expands to Body Mass Index."

score = get_similarity(model_out, expected)
print(f"Semantic Similarity Score: {score:.4f}")
# Output will likely be ~0.94+ because the meaning is identical
