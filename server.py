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

ESPN_SITE_API_BASE_URL = "https://site.api.espn.com"
ESPN_CORE_API_BASE_URL = "https://sports.core.api.espn.com"
ESPN_WEB_V3_API_BASE_URL = "https://site.web.api.espn.com"
ESPN_CDN_API_BASE_URL = "https://cdn.espn.com"
ESPN_NOW_API_BASE_URL = "https://now.core.api.espn.com"

DEFAULT_HEADERS = {
    "User-Agent": "ESPN-MCP-Service/1.0",
    "Accept": "application/json",
}


@mcp.tool()
async def get_scoreboard(
    sport: str,
    league: str,
    date: Optional[str] = None,
) -> dict:
    """Fetch live and recent sports scoreboards from ESPN for a given sport and league. Use this when the user asks about current scores, ongoing games, today's matchups, or recent game results."""
    url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/scoreboard"
    params = {}
    if date:
        params["dates"] = date
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_teams(
    sport: str,
    league: str,
    limit: int = 50,
) -> dict:
    """Retrieve a list of teams for a given sport and league from ESPN. Use this when the user wants to browse teams, find team information, or look up team IDs for further queries."""
    url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/teams"
    params = {"limit": limit}
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_athlete_stats(
    athlete_id: str,
    sport: str,
    league: str,
    stat_type: str = "season",
    season: Optional[str] = None,
) -> dict:
    """Fetch season stats, gamelogs, or career splits for a specific athlete from ESPN. Use this when the user asks about player statistics, performance metrics, or historical data for a player."""
    # Map stat_type to ESPN web v3 endpoint segments
    stat_type_map = {
        "season": "stats",
        "gamelog": "gamelog",
        "splits": "splits",
    }
    endpoint_segment = stat_type_map.get(stat_type, "stats")
    url = f"{ESPN_WEB_V3_API_BASE_URL}/apis/common/v3/sports/{sport}/{league}/athletes/{athlete_id}/{endpoint_segment}"
    params = {}
    if season:
        params["season"] = season
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Fallback: try site v2 athlete overview
            fallback_url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/athletes/{athlete_id}"
            try:
                fallback_response = await client.get(fallback_url)
                fallback_response.raise_for_status()
                return fallback_response.json()
            except Exception:
                return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_news(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    team_id: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """Retrieve sports news articles from ESPN for a specific sport, league, or team. Use this when the user asks for the latest news, headlines, or updates about a sport or team."""
    params = {"limit": limit}

    if sport and league and team_id:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/news"
        params["team"] = team_id
    elif sport and league:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/news"
    elif sport:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/news"
    else:
        # General ESPN news from now API
        url = f"{ESPN_NOW_API_BASE_URL}/v1/layout/news"

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_standings(
    sport: str,
    league: str,
    season: Optional[str] = None,
) -> dict:
    """Fetch current league standings from ESPN for a sport and league. Use this when the user asks about team rankings, conference standings, playoff pictures, or divisional standings."""
    url = f"{ESPN_SITE_API_BASE_URL}/apis/v2/sports/{sport}/{league}/standings"
    params = {}
    if season:
        params["season"] = season
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Fallback to site v2
            fallback_url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/standings"
            try:
                fallback_response = await client.get(fallback_url, params=params)
                fallback_response.raise_for_status()
                return fallback_response.json()
            except Exception:
                return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_injuries(
    sport: str,
    league: str,
    team_id: Optional[str] = None,
) -> dict:
    """Retrieve current injury reports for a sport and league from ESPN. Use this when the user asks about player injuries, injury status, or who is out/questionable for upcoming games."""
    if team_id:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/injuries"
    else:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/injuries"
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_game_details(
    event_id: str,
    sport: str,
    league: str,
    include_play_by_play: bool = False,
    include_odds: bool = False,
) -> dict:
    """Fetch detailed information about a specific ESPN game event including play-by-play, odds, drives, win probability, and box score. Use this when the user wants in-depth analysis of a specific game."""
    result = {}

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        # Summary / box score
        summary_url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/summary"
        try:
            summary_response = await client.get(summary_url, params={"event": event_id})
            summary_response.raise_for_status()
            result["summary"] = summary_response.json()
        except httpx.HTTPStatusError as e:
            result["summary_error"] = f"HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            result["summary_error"] = str(e)

        # Play-by-play
        if include_play_by_play:
            pbp_url = f"{ESPN_CDN_API_BASE_URL}/core/{sport}/{league}/playbyplay"
            try:
                pbp_response = await client.get(pbp_url, params={"xhr": 1, "gameId": event_id})
                pbp_response.raise_for_status()
                result["play_by_play"] = pbp_response.json()
            except httpx.HTTPStatusError as e:
                result["play_by_play_error"] = f"HTTP error {e.response.status_code}: {e.response.text}"
            except Exception as e:
                result["play_by_play_error"] = str(e)

        # Odds
        if include_odds:
            odds_url = f"{ESPN_CORE_API_BASE_URL}/v2/sports/{sport}/{league}/events/{event_id}/competitions/{event_id}/odds"
            try:
                odds_response = await client.get(odds_url)
                odds_response.raise_for_status()
                result["odds"] = odds_response.json()
            except httpx.HTTPStatusError as e:
                result["odds_error"] = f"HTTP error {e.response.status_code}: {e.response.text}"
            except Exception as e:
                result["odds_error"] = str(e)

    return result


@mcp.tool()
async def get_transactions(
    sport: str,
    league: str,
    team_id: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """Retrieve recent player transactions (trades, signings, waivers, releases) for a sport and league from ESPN. Use this when the user asks about player movements, roster changes, trades, or free agent signings."""
    if team_id:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/transactions"
    else:
        url = f"{ESPN_SITE_API_BASE_URL}/apis/site/v2/sports/{sport}/{league}/transactions"
    params = {"limit": limit}
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}: {e.response.text}"}
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
