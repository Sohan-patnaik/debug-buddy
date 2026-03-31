import lancedb
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_classic.schema import Document
from schemas.schema import CodeInput, WebSearch
from sources.gfg import scrape_gfg_article
from sources.stack import search_stackoverflow
from sources.nextjs import crawl_nextjs_docs
import asyncio

class Retrieve:
    def __init__(self,code,error):
        self.embedding = GoogleGenerativeAIEmbeddings(model="model-embedding-001")
        self.code_context = CodeInput(code,error)

    async def init_db(self):
        self.async_db = await lancedb.connect_async("ex_lancedb")

    async def web_search(self):
        results = []

      
        gfg = asyncio.to_thread(scrape_gfg_article(self.code_context.error))
        stack = asyncio.to_thread(search_stackoverflow(self.code_context.error))

        results.append(gfg)
        results.append(stack)

        async for url, content in crawl_nextjs_docs():
            results.append(content)

        return results

    async def store(self):
        web_results = await self.web_search()

        docs = [
            Document(page_content=str(content))
            for content in web_results
        ]

        vector_store = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding,
            collection_name="my_collection"
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": 2})

        query = self.code_context.code
        results = retriever.invoke(query)

        return results