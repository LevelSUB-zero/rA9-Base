"""
Search Agent for RA9.

This module provides search capabilities using various search engines.
"""

from typing import List, Dict, Any, Optional
from ..agents.base_agent import BaseAgent, AgentResult


class SearchAgent(BaseAgent):
    """Search agent for web and knowledge base searches."""
    
    def __init__(self):
        super().__init__(
            name="SearchAgent",
            description="Performs web searches and knowledge base queries"
        )
    
    def process_query(self, query: str, context: Dict[str, Any]) -> AgentResult:
        """Process a search query."""
        try:
            # Perform search
            results = self._perform_search(query)
            
            # Format results
            formatted_results = self._format_results(results)
            
            return AgentResult(
                answer=formatted_results,
                quality_score=8.0,
                confidence=0.9,
                reasoning="Search completed successfully",
                metadata={"search_results": results}
            )
            
        except Exception as e:
            return AgentResult(
                answer=f"Search failed: {str(e)}",
                quality_score=2.0,
                confidence=0.1,
                reasoning="Search encountered an error"
            )
    
    def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform the actual search."""
        # Mock search implementation
        return [
            {
                "title": f"Search Result 1 for: {query}",
                "snippet": "This is a simulated search result providing relevant information.",
                "url": "https://example.com/result1"
            },
            {
                "title": f"Search Result 2 for: {query}",
                "snippet": "Another simulated result offering a different perspective.",
                "url": "https://example.com/result2"
            },
            {
                "title": f"Search Result 3 for: {query}",
                "snippet": "A third simulated snippet completing the search results.",
                "url": "https://example.com/result3"
            }
        ]
    
    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into a readable response."""
        if not results:
            return "No search results found."
        
        formatted = "Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   URL: {result['url']}\n\n"
        
        return formatted.strip()


def do_search(query: str) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    agent = SearchAgent()
    results = agent._perform_search(query)
    return results