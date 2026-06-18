from dotenv import load_dotenv
import os 

load_dotenv()

RESEARCHER_PROMPT_PATH = "chat_agent\\prompts\\maestroresearcher.md"
MANAGER_PROMP_PATH = "chat_agent\\prompts\\maestromanager.md"

PAGE_FILE_PATH = "front\\agent-showcase.html"
BASE_PAGE_FILE_PATH = "front\\agent-showcase-base.html"

PROMPT_RESEARCHER_TAG = "<<<researcher-prompt>>>"
PROMPT_MANAGER_TAG = "<<manager-prompt>>>"
API_KEY_TAG = "<<<api-key>>>"

researcher_prompt = open(RESEARCHER_PROMPT_PATH, 'r', encoding="utf-8").read().replace("`", "'")
manager_prompt = open(MANAGER_PROMP_PATH, 'r', encoding="utf-8").read().replace("`", "'")

with open(BASE_PAGE_FILE_PATH, 'r', encoding="utf-8") as page:
    with open(PAGE_FILE_PATH, 'w', encoding="utf-8") as new_page:
        new_page.write(page.read().replace(PROMPT_RESEARCHER_TAG, researcher_prompt).replace(PROMPT_MANAGER_TAG, manager_prompt).replace(API_KEY_TAG, os.getenv("GROQ_KEY")))