import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

# BBC News Homepage
BASE_URL = "https://www.bbc.com/news"

# Function to get article links from the BBC homepage
def get_bbc_articles(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    article_links = set()

    # Find all article links (links that start with /news/)
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("/news") and ":" not in href:  # Ignore external links
            full_url = f"https://www.bbc.com{href}"
            article_links.add(full_url)
    
    return list(article_links)

# Get top articles from BBC News homepage
bbc_articles = get_bbc_articles(BASE_URL)
print(f"Found {len(bbc_articles)} articles.")


def get_internal_links(article_url):
    """Extract internal links from a BBC article."""
    response = requests.get(article_url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    internal_links = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("/news") and ":" not in href:  # Ensure it's an internal BBC News link
            full_url = f"https://www.bbc.com{href}"
            internal_links.add(full_url)
    
    return list(internal_links)

# Create a directed graph
G = nx.DiGraph()

# Limit crawling to avoid excessive requests
MAX_ARTICLES = 10  
for article in bbc_articles[:MAX_ARTICLES]:
    internal_links = get_internal_links(article)
    
    # Add edges (current article → linked articles)
    for link in internal_links:
        G.add_edge(article, link)

print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

# Compute PageRank
pagerank_scores = nx.pagerank(G)
top_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:5]

# Compute In-Degree Centrality
in_degree = dict(G.in_degree())
top_in_degree = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]

# Compute Betweenness Centrality
betweenness = nx.betweenness_centrality(G)
top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]

# Print the most important articles
print("\nTop Articles by PageRank:")
for url, score in top_pagerank:
    print(f"{url} - PageRank: {score:.4f}")

print("\nTop Articles by In-Degree Centrality:")
for url, degree in top_in_degree:
    print(f"{url} - In-Degree: {degree}")

print("\nTop Articles by Betweenness Centrality:")
for url, score in top_betweenness:
    print(f"{url} - Betweenness: {score:.4f}")

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42)  # Positioning algorithm

# Scale node size by PageRank score
node_size = [pagerank_scores[node] * 3000 for node in G.nodes()]

nx.draw(G, pos, with_labels=False, node_color="skyblue", edge_color="gray",
        node_size=node_size, alpha=0.7, arrows=True)

plt.title("BBC News Internal Link Network")
plt.show()
