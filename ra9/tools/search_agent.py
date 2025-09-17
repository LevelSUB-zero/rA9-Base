def do_search(query):
    # return top 3 results (mock first, add real later)
    print(f"Performing mock search for: {query}")
    return [
        {"title": f"Mock Insight 1 for {query}", "snippet": "This is a simulated search result providing some relevant information."},
        {"title": f"Mock Insight 2 for {query}", "snippet": "Another simulated result, perhaps offering a different perspective."},
        {"title": f"Mock Insight 3 for {query}", "snippet": "A third simulated snippet that completes the search results."},
    ]