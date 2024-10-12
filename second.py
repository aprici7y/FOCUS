from notion_client import Client
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('NOTION_API_KEY')
print(API_KEY)
# Initialize the Notion client
notion = Client(auth=API_KEY)  # Replace with your token

# Define your parent page ID
# Replace with your parent page's Notion ID
parent_page_id = "118d3dc2-9328-805c-b056-ea4201a8dfc9"

# Function to create a page in Notion


def create_notion_page(parent_id, title, content):
    response = notion.pages.create(
        parent={"type": "page_id", "page_id": parent_id},
        properties={
            "title": [
                {
                    "type": "text",
                    "text": {"content": title},
                }
            ]
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content,
                            },
                        }
                    ]
                },
            }
        ],
    )
    return response


# Dummy content
lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

# Create the main page
main_page = create_notion_page(parent_page_id, "Main Page", lorem_ipsum)

# Create subpages under the main page
subpage1 = create_notion_page(main_page["id"], "Subpage 1", lorem_ipsum)
subpage2 = create_notion_page(main_page["id"], "Subpage 2", lorem_ipsum)
subpage3 = create_notion_page(main_page["id"], "Subpage 3", lorem_ipsum)

print("Pages created successfully!")
