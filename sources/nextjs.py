import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl_nextjs_docs():

    urls = [
        "https://github.com/vercel/next.js/blob/canary/docs/01-app/index.mdx",
        "https://github.com/vercel/next.js/blob/canary/docs/02-pages/index.mdx",
       # "https://github.com/vercel/next.js/blob/canary/docs/03-architecture/index.mdx"
    ]


    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(url=url)
            yield url, result.markdown

async def main():
    async for url, content in crawl_nextjs_docs():
        print(f"URL: {url}")
        print(content[:300] if content else "[No content found]")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())