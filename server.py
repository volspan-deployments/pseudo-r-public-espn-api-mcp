from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("ESPN Public API Service")

BASE_URL = "https://site.api.espn.com"


@mcp.tool()
async def check_health() -> dict:
    """Check the health and connectivity status of the ESPN service, including database connectivity. Use this to verify the service is running before making other requests, or to diagnose connectivity issues."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(f"{BASE_URL}/healthz")
            response.raise_for_status()
            return {"status": "ok", "code": response.status_code, "body": response.json()}
        except httpx.HTTPStatusError as e:
            return {"status": "error", "code": e.response.status_code, "body": e.response.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}


@mcp.tool()
async def list_sports_and_leagues(
    resource: str,
    id: Optional[int] = None
) -> dict:
    """Retrieve all available sports or leagues. Use this to discover what sports and leagues are supported by the service, or to find IDs/slugs needed for filtering other queries. Pass resource='sports' for sports or resource='leagues' for leagues."""
    if resource not in ("sports", "leagues"):
        return {"error": "resource must be 'sports' or 'leagues'"}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if id is not None:
                url = f"{BASE_URL}/api/{resource}/{id}/"
            else:
                url = f"{BASE_URL}/api/{resource}/"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def search_teams(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    is_active: Optional[bool] = None,
    abbreviation: Optional[str] = None,
    search: Optional[str] = None,
    id: Optional[int] = None
) -> dict:
    """List and filter sports teams. Use this to find teams by sport, league, name, abbreviation, or active status. Supports free-text search across team name, abbreviation, and location. Use this before querying events or stats when you need a team ID."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if id is not None:
                url = f"{BASE_URL}/api/teams/{id}/"
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            else:
                url = f"{BASE_URL}/api/teams/"
                params = {}
                if sport is not None:
                    params["sport"] = sport
                if league is not None:
                    params["league"] = league
                if is_active is not None:
                    params["is_active"] = str(is_active).lower()
                if abbreviation is not None:
                    params["abbreviation"] = abbreviation
                if search is not None:
                    params["search"] = search
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def search_events(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    date: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    season_year: Optional[int] = None,
    season_type: Optional[int] = None,
    team: Optional[str] = None,
    id: Optional[int] = None
) -> dict:
    """List and filter sports events/games. Use this to find games by sport, league, date range, status, season, or team. Essential for answering questions about schedules, scores, live games, or historical results. Status options: scheduled, in_progress, final, postponed, cancelled."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if id is not None:
                url = f"{BASE_URL}/api/events/{id}/"
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            else:
                url = f"{BASE_URL}/api/events/"
                params = {}
                if sport is not None:
                    params["sport"] = sport
                if league is not None:
                    params["league"] = league
                if date is not None:
                    params["date"] = date
                if date_from is not None:
                    params["date_from"] = date_from
                if date_to is not None:
                    params["date_to"] = date_to
                if status is not None:
                    params["status"] = status
                if season_year is not None:
                    params["season_year"] = season_year
                if season_type is not None:
                    params["season_type"] = season_type
                if team is not None:
                    params["team"] = team
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_athlete_info(
    resource: str,
    id: Optional[int] = None
) -> dict:
    """Retrieve athlete profiles and season statistics. Use this to look up player details, biographical information, or season stats. To get season statistics, use resource='stats'. To get athlete profile, use resource='athletes'."""
    if resource not in ("athletes", "stats"):
        return {"error": "resource must be 'athletes' or 'stats'"}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if resource == "athletes":
                if id is not None:
                    url = f"{BASE_URL}/api/athletes/{id}/"
                else:
                    url = f"{BASE_URL}/api/athletes/"
            else:  # stats
                if id is not None:
                    url = f"{BASE_URL}/api/athlete-season-stats/{id}/"
                else:
                    url = f"{BASE_URL}/api/athlete-season-stats/"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_injuries(
    id: Optional[int] = None
) -> dict:
    """Retrieve player injury records and reports. Use this to find out which players are injured, their injury status, and details about the injury. Useful for fantasy sports analysis or game preview research."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if id is not None:
                url = f"{BASE_URL}/api/injuries/{id}/"
            else:
                url = f"{BASE_URL}/api/injuries/"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_transactions(
    id: Optional[int] = None
) -> dict:
    """Retrieve player transaction records such as trades, signings, releases, and roster moves. Use this to find recent player movement between teams or roster changes."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if id is not None:
                url = f"{BASE_URL}/api/transactions/{id}/"
            else:
                url = f"{BASE_URL}/api/transactions/"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_news_and_venues(
    resource: str,
    id: Optional[int] = None
) -> dict:
    """Retrieve sports news articles or venue information. Use resource='news' to get sports news and articles. Use resource='venues' to get stadium and arena details. Useful for providing context about games, locations, or current events in sports."""
    if resource not in ("news", "venues"):
        return {"error": "resource must be 'news' or 'venues'"}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if id is not None:
                url = f"{BASE_URL}/api/{resource}/{id}/"
            else:
                url = f"{BASE_URL}/api/{resource}/"
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": e.response.text, "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e)}




_SERVER_SLUG = "pseudo-r-public-espn-api"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

sse_app = mcp.http_app(transport="sse")

app = Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", sse_app),
    ],
    lifespan=sse_app.lifespan,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
