from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from schemas.schema import CodeInput
from sources.gfg import scrape_gfg_article
from sources.stack import search_with_answers
from sources.nextjs import crawl_nextjs_docs
from core.logger import get_logger
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

logger = get_logger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
FRONTEND_KEYWORDS = {"jsx", "tsx", "next", "react", "component", "vue", "svelte"}

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


class Retrieve:
    def __init__(self, state: CodeInput) -> None:
        self.embedding = NVIDIAEmbeddings(
            model="nvidia/nv-embed-v1",
            api_key=os.getenv("NVIDIA_API_KEY"),
            truncate="END",  # safer than NONE — avoids token limit errors
        )
        self.code_context = state

    def _is_frontend_error(self) -> bool:
        combined = (self.code_context.error + self.code_context.code).lower()
        return any(kw in combined for kw in FRONTEND_KEYWORDS)

    def _clean(self, text: str) -> str:
        """Strip HTML entities and excessive whitespace."""
        import html
        return " ".join(html.unescape(text).split())

    async def _web_search(self) -> list[Document]:
        logger.info(f"Starting web search for error: {self.code_context.error[:80]}")

        # dynamic GFG search based on actual error
        gfg_query = f"python {self.code_context.error}"
        gfg_task = asyncio.to_thread(scrape_gfg_article, gfg_query)
        stack_task = asyncio.to_thread(search_with_answers, self.code_context.error)

        gfg_result, stack_result = await asyncio.gather(
            gfg_task, stack_task, return_exceptions=True
        )

        raw_docs: list[Document] = []

        if isinstance(gfg_result, Exception):
            logger.warning(f"GFG scrape failed: {gfg_result}")
        elif gfg_result:
            content = self._clean(str(gfg_result))
            if len(content) > 100:  # skip empty/useless results
                raw_docs.append(Document(page_content=content, metadata={"source": "gfg"}))
                logger.info("GFG: added document")

        if isinstance(stack_result, Exception):
            logger.warning(f"StackOverflow search failed: {stack_result}")
        elif stack_result:
            items = stack_result if isinstance(stack_result, list) else [stack_result]
            for item in items:
                content = self._clean(str(item))
                if len(content) > 50:
                    raw_docs.append(Document(
                        page_content=content,
                        metadata={"source": "stackoverflow"}
                    ))
            logger.info(f"StackOverflow: added {len(items)} document(s)")

        if self._is_frontend_error():
            logger.info("Frontend error detected — crawling Next.js docs")
            async for url, content in crawl_nextjs_docs():
                if content:
                    raw_docs.append(Document(
                        page_content=self._clean(str(content)),
                        metadata={"source": "nextjs", "url": url}
                    ))

        if not raw_docs:
            logger.warning("No documents retrieved — falling back to code-only context")
            raw_docs.append(Document(
                page_content=self.code_context.code,
                metadata={"source": "fallback"}
            ))

        chunked = splitter.split_documents(raw_docs)
        logger.info(f"Total chunks after splitting: {len(chunked)}")
        return chunked

    async def store(self) -> list[Document]:
        chunked_docs = await self._web_search()

        vector_store = Chroma.from_documents(
            documents=chunked_docs,
            embedding=self.embedding,
            collection_name="debug_buddy_collection",
            persist_directory="./chroma_db",
        )

        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 10},
        )

        query = self.code_context.error or self.code_context.code
        results = retriever.invoke(query)
        logger.info(f"Retrieved {len(results)} relevant chunks")
        return results