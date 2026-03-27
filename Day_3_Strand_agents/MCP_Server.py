import re
import httpx
from mcp.server.fastmcp import FastMCP

from utils import setup_run_logger

logger = setup_run_logger("logs", "mcp_tools")

class WikipediaUniversityTool:
    """MCP server exposing Wikipedia tools for university lookup."""

    WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
    WIKIPEDIA_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary"

    def __init__(self):
        self.mcp = FastMCP("wikipedia-university") 
        self.headers = {
            "User-Agent": "UniversityResearchBot/1.0 (contact: your-email@example.com)",
            "Accept": "application/json",
        }
        self.register_tools()

    def _clean_wikitext_value(self, value):
        if not value:
            return None

        cleaned = value
        cleaned = re.sub(r"<ref.*?>.*?</ref>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<ref.*?/>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"\{\{.*?\}\}", "", cleaned)
        cleaned = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", cleaned)
        cleaned = re.sub(r"\[\[([^\]]+)\]\]", r"\1", cleaned)
        cleaned = cleaned.replace("'''", "").replace("''", "")
        cleaned = re.sub(r"<.*?>", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned or None

    def _extract_infobox_value(self, text, keys):
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            lowered = stripped.lower()

            for key in keys:
                key_lower = key.lower()
                if lowered.startswith(f"| {key_lower}") or lowered.startswith(f"|{key_lower}"):
                    parts = stripped.split("=", 1)
                    if len(parts) == 2:
                        return self._clean_wikitext_value(parts[1].strip())
        return None

    def register_tools(self):
        @self.mcp.tool(
            name="search_wikipedia_page",
            description="Search Wikipedia for the best matching university page and return compact results.",
        )
        async def search_wikipedia_page(university_name: str) -> dict:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": university_name,
                "format": "json",
                "utf8": 1,
                "srlimit": 5,
            }

            async with httpx.AsyncClient(
                timeout=20.0,
                headers=self.headers,
                follow_redirects=True,
            ) as client:
                response = await client.get(self.WIKIPEDIA_API, params=params)
                response.raise_for_status()
                data = response.json()

            results = data.get("query", {}).get("search", [])
            compact_results = []

            for item in results:
                title = item.get("title")
                compact_results.append(
                    {
                        "title": title,
                        "snippet": self._clean_wikitext_value(item.get("snippet", "")),
                        "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}" if title else None,
                    }
                )

            result = {
                "query": university_name,
                "count": len(compact_results),
                "results": compact_results,
            }

            logger.info(f"TOOL OUTPUT [search_wikipedia_page]: {result}")
            return result

        @self.mcp.tool(
            name="get_wikipedia_university_info",
            description="Get compact structured university information from a Wikipedia page title.",
        )
        async def get_wikipedia_university_info(page_title: str) -> dict:
            safe_title = page_title.replace(" ", "_")
            summary_url = f"{self.WIKIPEDIA_SUMMARY_API}/{safe_title}"

            revision_params = {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "titles": page_title,
                "format": "json",
                "formatversion": 2,
            }

            async with httpx.AsyncClient(
                timeout=20.0,
                headers=self.headers,
                follow_redirects=True,
            ) as client:
                summary_response = await client.get(summary_url)
                summary_response.raise_for_status()
                summary_data = summary_response.json()

                revision_response = await client.get(self.WIKIPEDIA_API, params=revision_params)
                revision_response.raise_for_status()
                revision_data = revision_response.json()

            page = (revision_data.get("query", {}).get("pages") or [{}])[0]
            revisions = page.get("revisions") or [{}]
            raw_content = revisions[0].get("slots", {}).get("main", {}).get("content", "")

            founded = self._extract_infobox_value(raw_content, ["established", "founded"])
            institution_type = self._extract_infobox_value(raw_content, ["type"])
            city = self._extract_infobox_value(raw_content, ["city"])
            state = self._extract_infobox_value(raw_content, ["state"])
            country = self._extract_infobox_value(raw_content, ["country"])
            campus = self._extract_infobox_value(raw_content, ["campus"])
            students = self._extract_infobox_value(raw_content, ["students"])
            president = self._extract_infobox_value(raw_content, ["president"])
            chancellor = self._extract_infobox_value(raw_content, ["chancellor"])

            location_parts = [part for part in [city, state, country] if part]
            location = ", ".join(location_parts) if location_parts else None

            result = {
            "page_title": summary_data.get("title", page_title),
            "wikipedia_url": summary_data.get("content_urls", {}).get("desktop", {}).get("page"),
            "summary": summary_data.get("extract"),
            "description": summary_data.get("description"),
            "founded": founded,
            "type": institution_type,
            "location": location,
            "campus_setting": campus,
            "student_enrollment": students,
            "president": president,
            "chancellor": chancellor,
            "source": "Wikipedia",
            }

            logger.info(f"TOOL OUTPUT [get_wikipedia_university_info]: {result}")
            return result

    def run(self, host: str = "127.0.0.1", port: int = 8000):

        import uvicorn

        app = self.mcp.streamable_http_app()
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    server = WikipediaUniversityTool()
    server.run(host="127.0.0.1", port=8000)