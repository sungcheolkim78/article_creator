import dspy
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime


class ReactMemory:
    """Memory system for ReACT agent to maintain context and search sources across iterations."""

    def __init__(self, max_memory_size: int = 1000):
        self.max_memory_size = max_memory_size
        self.memory_store = {
            "search_results": {},  # Store search results by query hash
            "research_findings": {},  # Store research findings by topic
            "fact_checks": {},  # Store fact verification results
            "context": [],  # Store contextual information
            "sources": {},  # Store source URLs and metadata
            "insights": [],  # Store key insights and learnings
            "action_history": [],  # Store action patterns and outcomes
        }
        self.access_count = {}  # Track access frequency for memory management

    def add_search_result(self, query: str, results: List[Dict], metadata: Dict = None):
        """Add search results to memory with query as key."""
        query_hash = self._hash_query(query)
        self.memory_store["search_results"][query_hash] = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "access_count": 0,
        }
        self._manage_memory_size()

    def add_research_finding(self, topic: str, finding: Dict):
        """Add research finding to memory."""
        topic_hash = self._hash_query(topic)
        if topic_hash not in self.memory_store["research_findings"]:
            self.memory_store["research_findings"][topic_hash] = []

        self.memory_store["research_findings"][topic_hash].append(
            {
                "finding": finding,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
            }
        )
        self._manage_memory_size()

    def add_fact_check(self, claim: str, verification: Dict):
        """Add fact check result to memory."""
        claim_hash = self._hash_query(claim)
        self.memory_store["fact_checks"][claim_hash] = {
            "claim": claim,
            "verification": verification,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        self._manage_memory_size()

    def add_context(self, context: str, relevance_score: float = 1.0):
        """Add contextual information to memory."""
        self.memory_store["context"].append(
            {
                "context": context,
                "relevance_score": relevance_score,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
            }
        )
        self._manage_memory_size()

    def add_source(self, url: str, source_info: Dict):
        """Add source information to memory."""
        url_hash = self._hash_query(url)
        self.memory_store["sources"][url_hash] = {
            "url": url,
            "info": source_info,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        self._manage_memory_size()

    def add_insight(self, insight: str, category: str = "general"):
        """Add key insight to memory."""
        self.memory_store["insights"].append(
            {
                "insight": insight,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
            }
        )
        self._manage_memory_size()

    def get_relevant_search_results(
        self, query: str, max_results: int = 5
    ) -> List[Dict]:
        """Retrieve relevant search results based on query similarity."""
        query_hash = self._hash_query(query)

        # Direct match
        if query_hash in self.memory_store["search_results"]:
            result = self.memory_store["search_results"][query_hash]
            result["access_count"] += 1
            return [result]

        # Similarity search (simple keyword matching for now)
        relevant_results = []
        query_lower = query.lower()

        for stored_query_hash, stored_result in self.memory_store[
            "search_results"
        ].items():
            stored_query = stored_result["query"].lower()
            # Simple keyword overlap check
            query_words = set(query_lower.split())
            stored_words = set(stored_query.split())
            overlap = len(query_words.intersection(stored_words))

            if overlap > 0:
                stored_result["access_count"] += 1
                relevant_results.append(stored_result)

        # Sort by relevance (overlap) and recency
        relevant_results.sort(
            key=lambda x: (
                len(
                    set(query_lower.split()).intersection(
                        set(x["query"].lower().split())
                    )
                ),
                x["timestamp"],
            ),
            reverse=True,
        )

        return relevant_results[:max_results]

    def get_research_findings(self, topic: str) -> List[Dict]:
        """Retrieve research findings for a topic."""
        topic_hash = self._hash_query(topic)
        if topic_hash in self.memory_store["research_findings"]:
            findings = self.memory_store["research_findings"][topic_hash]
            for finding in findings:
                finding["access_count"] += 1
            return findings
        return []

    def get_fact_check(self, claim: str) -> Optional[Dict]:
        """Retrieve fact check result for a claim."""
        claim_hash = self._hash_query(claim)
        if claim_hash in self.memory_store["fact_checks"]:
            result = self.memory_store["fact_checks"][claim_hash]
            result["access_count"] += 1
            return result
        return None

    def get_relevant_context(self, query: str, max_context: int = 3) -> List[str]:
        """Retrieve relevant contextual information."""
        query_lower = query.lower()
        relevant_contexts = []

        for context_item in self.memory_store["context"]:
            context_lower = context_item["context"].lower()
            # Simple keyword matching
            query_words = set(query_lower.split())
            context_words = set(context_lower.split())
            overlap = len(query_words.intersection(context_words))

            if overlap > 0:
                context_item["access_count"] += 1
                relevant_contexts.append(context_item)

        # Sort by relevance and recency
        relevant_contexts.sort(
            key=lambda x: (x["relevance_score"], x["timestamp"]), reverse=True
        )

        return [item["context"] for item in relevant_contexts[:max_context]]

    def get_recent_insights(
        self, category: str = None, max_insights: int = 5
    ) -> List[str]:
        """Retrieve recent insights, optionally filtered by category."""
        insights = self.memory_store["insights"]
        if category:
            insights = [
                insight for insight in insights if insight["category"] == category
            ]

        # Sort by recency
        insights.sort(key=lambda x: x["timestamp"], reverse=True)

        for insight in insights[:max_insights]:
            insight["access_count"] += 1

        return [insight["insight"] for insight in insights[:max_insights]]

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of memory contents."""
        return {
            "total_search_results": len(self.memory_store["search_results"]),
            "total_research_findings": sum(
                len(findings)
                for findings in self.memory_store["research_findings"].values()
            ),
            "total_fact_checks": len(self.memory_store["fact_checks"]),
            "total_context_items": len(self.memory_store["context"]),
            "total_sources": len(self.memory_store["sources"]),
            "total_insights": len(self.memory_store["insights"]),
            "memory_size": self._get_memory_size(),
        }

    def _hash_query(self, query: str) -> str:
        """Create a hash for a query string."""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_memory_size(self) -> int:
        """Calculate current memory size."""
        total_size = 0
        for category, items in self.memory_store.items():
            if isinstance(items, dict):
                total_size += len(items)
            elif isinstance(items, list):
                total_size += len(items)
        return total_size

    def _manage_memory_size(self):
        """Manage memory size by removing least accessed items if needed."""
        current_size = self._get_memory_size()

        if current_size <= self.max_memory_size:
            return

        # Remove least accessed items from each category
        for category, items in self.memory_store.items():
            if isinstance(items, dict):
                # Sort by access count and remove least accessed
                sorted_items = sorted(
                    items.items(), key=lambda x: x[1].get("access_count", 0)
                )
                items_to_remove = current_size - self.max_memory_size
                for i in range(min(items_to_remove, len(sorted_items))):
                    del items[sorted_items[i][0]]
            elif isinstance(items, list):
                # Sort by access count and remove least accessed
                items.sort(key=lambda x: x.get("access_count", 0))
                items_to_remove = current_size - self.max_memory_size
                if items_to_remove > 0:
                    self.memory_store[category] = items[items_to_remove:]
