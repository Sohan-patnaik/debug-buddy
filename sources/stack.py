import requests

def search_stackoverflow(query: str, tag: str = "next.js") -> list[dict]:
    url = "https://api.stackexchange.com/2.3/search/advanced"

    params = {
        "order": "desc",
        "sort": "votes",
        "q": query,                 # 🔥 use query
        "tagged": tag,              # 🔥 use dynamic tag
        "site": "stackoverflow",
        "filter": "withbody",
        "pagesize": 5
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            results.append({
                "title": item["title"],
                "question": item["body"],
                "question_id": item["question_id"],
                "link": item["link"]
            })

        return results

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return []
    

def get_answers(question_id: int) -> list[dict]:
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"

    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "filter": "withbody"
    }

    response = requests.get(url, params=params)
    data = response.json()

    answers = []
    for item in data.get("items", []):
        answers.append({
            "answer": item["body"],
            "is_accepted": item["is_accepted"],
            "score": item["score"]
        })

    return answers


def search_with_answers(query: str, tag: str = "next.js"):
    questions = search_stackoverflow(query, tag)

    enriched_data = []

    for q in questions:
        answers = get_answers(q["question_id"])

        enriched_data.append({
            "title": q["title"],
            "question": q["question"],
            "answers": answers,
            "link": q["link"]
        })

    return enriched_data