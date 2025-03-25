import os
import requests
import markdown
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# ✅ Use SerpAPI for Reliable Google Search
SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Get from https://serpapi.com/
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing. Set it in your environment variables.")

if not SERPAPI_KEY:
    raise ValueError("❌ SERPAPI_KEY is missing. Set it in your environment variables.")

# 1️⃣ Research Agent: Get Trending HR Topics via SerpAPI
class ResearchAgent:
    def __init__(self):
        self.url = "https://serpapi.com/search"

    def fetch_trending_topics(self):
        print("📌 Fetching trending HR topics...")

        params = {
            "engine": "google_news",
            "q": "HR trends",
            "api_key": SERPAPI_KEY,
        }

        try:
            response = requests.get(self.url, params=params)
            if response.status_code != 200:
                print(f"❌ Request failed with status code: {response.status_code}")
                return []

            news_data = response.json()
            articles = news_data.get("news_results", [])

            topics = [article["title"] for article in articles if "title" in article]

            if not topics:
                print("❌ No topics found. Check SerpAPI response.")
                return []

            return topics[:5]  # Return top 5 topics

        except Exception as e:
            print(f"❌ Error fetching topics: {e}")
            return []

# 2️⃣ Writer Agent: Generate HR Research Summaries using OpenAI
class WriterAgent:
    def __init__(self, model):
        self.model = model

    def generate_content(self, topic):
        print(f"📝 Generating content for: {topic}")
        try:
            response = self.model.invoke([HumanMessage(content=f"Write a research summary on: {topic}")])
            return response.content
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return None

# 3️⃣ Editor Agent: Format output into Markdown
class EditorAgent:
    def format_as_markdown(self, topic, content):
        return f"# {topic}\n\n{content}\n"

# 4️⃣ Storage Agent: Save content to a Markdown file
class StorageAgent:
    def save_to_file(self, filename, content):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"📁 Content saved to {filename}")

# 🔹 Main Function
def main():
    model = ChatOpenAI(api_key=OPENAI_API_KEY)
    research_agent = ResearchAgent()
    writer_agent = WriterAgent(model)
    editor_agent = EditorAgent()
    storage_agent = StorageAgent()

    # Fetch HR topics
    topics = research_agent.fetch_trending_topics()
    if not topics:
        print("❌ No trending HR topics found. Exiting.")
        return

    selected_topic = topics[0]  # Choose first topic
    print(f"✅ Selected topic: {selected_topic}")

    # Generate research content
    content = writer_agent.generate_content(selected_topic)
    if not content:
        print("❌ Failed to generate content. Exiting.")
        return

    # Format in Markdown
    formatted_content = editor_agent.format_as_markdown(selected_topic, content)

    # Save to a file
    storage_agent.save_to_file("HR_Research.md", formatted_content)

    print("🎉 Research saved successfully!")

if __name__ == "__main__":
    main()
