
from datetime import datetime
from pathlib import Path
import os

from notion_client import Client
import re

from creation_stratgey import CreationStrategy

# Obsidian Strategy Class


def sanitize_title(title):
    # Replace any character that is not a word character or a space with an underscore
    # Replace non-word and non-space characters
    sanitized_title = re.sub(r'[^\w\s]', '_', title)
    # Replace spaces with underscores
    sanitized_title = sanitized_title.replace(' ', '_')
    return sanitized_title


class ObsidianStrategy(CreationStrategy):
    def __init__(self, vault_path):
        self.vault_path = vault_path

    def create_summary_file(self, title, content):
        file_name = f"{sanitize_title(title)}.md"
        file_path = Path(self.vault_path) / file_name
        markdown_content = f"# {title}\n\n{content}\n\n---\n\nCreated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        # Write the content to the Markdown file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)

    def create(self, playlist_title, video_summaries):
        # Create the main playlist note
        main_note_title = sanitize_title(playlist_title)
        main_note_path = Path(self.vault_path) / f"{main_note_title}.md"

        # Create content for the main note
        main_content = f"# {playlist_title}\n\nThis playlist contains the following videos:\n\n"

        # Create subnotes for each video summary and link them in the main note
        for video in video_summaries:
            video_title = video['title']
            video_summary = video['summary']
            self.create_summary_file(video_title, video_summary)
            # Link to the subnote in the main note
            main_content += f"- [[{sanitize_title(video_title)}]]\n"

        # Write the main note
        with open(main_note_path, 'w', encoding='utf-8') as file:
            file.write(main_content)


# Notion Strategy Class
class NotionStrategy(CreationStrategy):
    def __init__(self, notion_api_key, parent_page_id):
        self.notion = Client(auth=notion_api_key)
        self.parent_page_id = parent_page_id

    def create_page(self, title, content):
        def split_content(text, max_length=2000):
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = []

            for paragraph in paragraphs:
                if len('\n\n'.join(current_chunk + [paragraph])) <= max_length:
                    current_chunk.append(paragraph)
                else:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [paragraph]

            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))

            return chunks

        content_chunks = split_content(content)
        children = self.create_blocks(content_chunks)

        response = self.notion.pages.create(
            parent={"type": "page_id", "page_id": self.parent_page_id},
            properties={
                "title": [{"type": "text", "text": {"content": title}}]
            },
            children=children,
        )
        return response

    def create_blocks(self, content):
        blocks = []
        if isinstance(content, str):
            lines = content.split('\n')
        else:
            lines = content

        for line in lines:
            line = line.strip() if isinstance(line, str) else line
            if line:
                if line.startswith('**') and line.endswith('**'):
                    blocks.append({
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"type": "text", "text": {"content": line.strip('**')}}]
                        }
                    })
                elif line.startswith('- '):
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                        }
                    })
                else:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": line}}]
                        }
                    })

        return blocks

    def create(self, playlist_title, video_summaries):
        # Create the main playlist page
        main_page = self.create_page(
            playlist_title, "This page contains summaries of videos in the playlist.")

        # Create subpages for each video summary under the main page
        for video in video_summaries:
            video_title = video['title']
            video_summary = video['summary']
            self.create_page(video_title, video_summary)


class NoteAppProcessor:
    def __init__(self, strategy: CreationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: CreationStrategy):
        self._strategy = strategy

    def process_playlist(self, playlist_title, video_summaries):
        self._strategy.create(playlist_title, video_summaries)
