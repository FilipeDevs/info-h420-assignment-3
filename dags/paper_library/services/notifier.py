import requests

from paper_library.models import PaperMetadata


class DiscordNotifier:
    """
    Posts a message to a Discord channel through a webhook.
    """
    TIMEOUT_SECONDS = 10

    def __init__(self, webhook_url: str | None):
        self.webhook_url = webhook_url

    def notify_new_paper(self, filename: str, metadata: PaperMetadata) -> bool:
        if not self.webhook_url:
            print("DISCORD_WEBHOOK_URL is not set, skipping the notification")
            return False

        message = self.build_message(filename, metadata)
        response = requests.post(self.webhook_url, json=message, timeout=self.TIMEOUT_SECONDS)

        # raise on an HTTP error so the task fails and Airflow retries it
        response.raise_for_status()
        return True

    def build_message(self, filename: str, metadata: PaperMetadata) -> dict:
        keywords_text = ", ".join(metadata.keywords)
        if not keywords_text:
            keywords_text = "-"
        return {
            "content": "New paper added to the library",
            "embeds": [
                {
                    "title": metadata.title[:256], # discord limits
                    "description": metadata.summary[:4000], # discord limits
                    "fields": [
                        {"name": "Category", "value": metadata.category, "inline": True},
                        {"name": "File", "value": filename, "inline": True},
                        {"name": "Keywords", "value": keywords_text[:1024]},
                    ],
                }
            ],
        }
