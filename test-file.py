#!/usr/bin/env python3
"""
Exa API Test Script
This script tests the Exa API functionality with LinkedIn search queries.
Before running, make sure to replace 'your_exa_api_key_here' with your actual Exa API key.
"""

from exa_py import Exa

# Initialize Exa client with your API key
# Get your API key from: https://exa.ai/
exa = Exa(api_key = "your_exa_api_key_here")

# Example: Search for Credit Portfolio Managers at LIC
# This demonstrates how to create a dorked LinkedIn search query
result = exa.search_and_contents(
  f'"intitle:"Credit Portfolio Manager" AND ("LIC" OR "@LIC" OR "| LIC" OR "- LIC" OR "at LIC" OR "(LIC)" OR ": LIC") inurl:/in/"',
  text = True,
  exclude_text = ["linkedin.com/company"],  # Exclude company pages
  include_text = ["linkedin.com/in"],       # Include only profile pages
  num_results = 5,
  include_domains = ["linkedin.com"],
  livecrawl = "fallback",
  extras = {
    "links": 1
  },
  category = "linkedin profile"
)

# Print the results
print("🔍 Search Results:")
print("=" * 50)
print(result)