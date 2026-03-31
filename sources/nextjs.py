import asyncio
from crawl4ai import AsyncWebCrawler


async def crawl_nextjs_docs():
    urls = [
        "https://nextjs.org/docs/app/building-your-application/routing",
        "https://nextjs.org/docs/app/building-your-application/data-fetching",
    ]

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(url=url)
            yield url, result.markdown


async def main():
    async for url, content in crawl_nextjs_docs():
        print(f"URL: {url}")
        print(content[:200])

if __name__ == "__main__":
    asyncio.run(main())
