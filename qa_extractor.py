import os
import json
import csv
import re
from bs4 import BeautifulSoup

# CONFIG
INPUT_FOLDER = "discourse_data"
OUTPUT_CSV = "cleaned_qa.csv"
MIN_ANSWER_LENGTH = 80  # Only treat long replies as likely answers

def clean_text(html):
    return BeautifulSoup(html, "html.parser").get_text().strip()

def looks_like_question(line):
    return '?' in line or re.match(r'^\d+\.\s+', line.strip())

def is_likely_answer(text):
    return len(text) >= MIN_ANSWER_LENGTH and text.count('?') <= 1

def extract_qa_from_thread(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("post_stream", {}).get("posts", [])
    topic_url = data.get("_actual_url", "")
    topic_title = data.get("title", "")

    qa_pairs = []
    pending_questions = []

    for post in posts:
        post_number = post["post_number"]
        author = post["username"]
        text = clean_text(post["cooked"])
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        url = f"{topic_url}/{post_number}"

        # If post has question-like lines
        question_lines = [line for line in lines if looks_like_question(line)]
        if question_lines:
            for q in question_lines:
                pending_questions.append({
                    "question": q,
                    "answer": "",
                    "thread_title": topic_title,
                    "url": url
                })
            continue

        # If it's a likely answer and there are pending questions
        if is_likely_answer(text) and pending_questions:
            # Match with the oldest unanswered question
            for qa in pending_questions:
                if qa["answer"] == "":
                    qa["answer"] = text
                    break

    # Return only completed QA pairs
    return [qa for qa in pending_questions if qa["answer"]]

def process_all_threads(input_folder, output_csv):
    all_qa = []
    for filename in os.listdir(input_folder):
        if filename.startswith("thread_") and filename.endswith(".json"):
            path = os.path.join(input_folder, filename)
            try:
                qa = extract_qa_from_thread(path)
                all_qa.extend(qa)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    # Write to CSV
    with open(output_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer", "thread_title", "url"])
        writer.writeheader()
        for row in all_qa:
            writer.writerow(row)

    print(f"Done! Extracted {len(all_qa)} clean QA pairs to {output_csv}")

if __name__ == "__main__":
    process_all_threads(INPUT_FOLDER, OUTPUT_CSV)
