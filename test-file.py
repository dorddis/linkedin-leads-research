#!/usr/bin/env python3
"""
Exa API Test Script
This script tests the Exa API functionality with LinkedIn search queries.
Before running, make sure to set up your .env file with your Exa API key.
"""

import os
from exa_py import Exa
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Exa client with your API key
# Get your API key from: https://exa.ai/
exa = Exa(api_key = os.getenv('EXA_API_KEY', 'your_exa_api_key_here'))

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