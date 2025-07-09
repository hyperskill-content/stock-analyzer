import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()

    base_url = os.getenv("BASE_URL")
    base_url = base_url.replace("openai", "assistants")

    api_key = os.getenv("OPENAI_API_KEY")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    r = requests.get(base_url, headers=headers)
    r.raise_for_status()
    data = r.json()
    if not data or "data" not in data or type(data["data"]) is not list or not data["data"]:
        print("No assistants found.")
        return
    for assistant in data["data"]:
        assistant_id = assistant.get("id")
        if not assistant_id:
            print("No ID found for assistant.")
            continue

        delete_url = f"{base_url}/{assistant_id}"
        delete_response = requests.delete(delete_url, headers=headers)
        delete_response.raise_for_status()
        print(f"Deleted assistant with ID: {assistant_id}")


if __name__ == "__main__":
    main()
