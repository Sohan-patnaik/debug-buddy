import httpx

def search_stackoverflow(query: str, tag: str = "next.js") -> list[dict]:
    resp = httpx.get("https://api.stackexchange.com/2.3/search/advanced", params={
        "q": query,
        "tagged": tag,
        "site": "stackoverflow",
        "filter": "withbody",       
        "sort": "votes",
        "min": 5,                  
        "pagesize": 5,
        "key": "rl_XH6qLhAvNuJ348oPWUX9on9Dc"      
    })
    return resp.json()["items"]