#!/usr/bin/env python3
"""
LinkedIn Lead Research Generator
This script implements the complete flow from user query to dorked search queries.

IMPORTANT: Before running this script, you MUST configure your API keys below!
- Replace 'your_groq_api_key_here' with your actual Groq API key
- Replace 'your_exa_api_key_here' with your actual Exa API key

See README.md for detailed setup instructions.
"""

import os
import json
import requests
import sys
import sqlite3
import time
from datetime import datetime
from exa_py import Exa

# =============================================================================
# API CONFIGURATION - REPLACE THESE PLACEHOLDER KEYS WITH YOUR ACTUAL API KEYS
# =============================================================================

# Groq API configuration
GROQ_API_KEY = 'your_groq_api_key_here'
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

# Exa API configuration
EXA_API_KEY = 'your_exa_api_key_here'
exa = Exa(api_key=EXA_API_KEY)

# Database configuration
DB_NAME = 'linkedin_leads.db'

def init_database():
    """Initialize SQLite database for storing search results"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            title TEXT,
            url TEXT,
            snippet TEXT,
            published_date TEXT,
            author TEXT,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT NOT NULL,
            total_queries INTEGER,
            queries_searched INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def save_search_results(query, results):
    """Save search results to database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for result in results:
        cursor.execute('''
            INSERT INTO search_results 
            (query, title, url, snippet, published_date, author, score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            query,
            result.title if hasattr(result, 'title') else '',
            result.url if hasattr(result, 'url') else '',
            result.text if hasattr(result, 'text') else '',
            result.published_date if hasattr(result, 'published_date') else '',
            result.author if hasattr(result, 'author') else '',
            result.score if hasattr(result, 'score') else 0.0
        ))
    
    conn.commit()
    conn.close()

def save_search_session(user_query, total_queries, queries_searched):
    """Save search session information"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO search_sessions 
        (user_query, total_queries, queries_searched)
        VALUES (?, ?, ?)
    ''', (user_query, total_queries, queries_searched))
    
    conn.commit()
    conn.close()

def call_exa_api(query, num_results=10):
    """Call Exa API to search for results"""
    try:
        print(f"🔍 Searching Exa API for: {query[:100]}...")
        
        result = exa.search_and_contents(
            query,
            text=True,
            exclude_text=["linkedin.com/company"],
            include_text=["linkedin.com/in"],
            num_results=num_results,
            include_domains=["linkedin.com"],
            livecrawl="fallback",
            extras={
                "links": 1
            },
            category="linkedin profile"
        )
        
        results = result.results
        print(f"✅ Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"❌ Error calling Exa API: {str(e)}")
        return []

def search_with_rate_limiting(queries, user_query):
    """Search queries with rate limiting - only first 5 out of every 20 queries"""
    total_queries = len(queries)
    queries_searched = 0
    total_results = 0
    
    print(f"\n🔍 Starting Exa API searches with rate limiting...")
    print(f"📊 Total queries: {total_queries}")
    print(f"📋 Search pattern: First 5 out of every 20 queries")
    print("=" * 60)
    
    for i, query in enumerate(queries):
        # Check if this query should be searched (first 5 out of every 20)
        position_in_batch = i % 20
        should_search = position_in_batch < 5
        
        if should_search:
            queries_searched += 1
            print(f"\n🔍 Query {queries_searched}/{total_queries} (Position {i+1})")
            
            # Call Exa API
            results = call_exa_api(query, num_results=10)
            
            if results:
                # Save results to database
                save_search_results(query, results)
                total_results += len(results)
                print(f"💾 Saved {len(results)} results to database")
            
            # Rate limiting - wait 1 second between searches
            if queries_searched < min(5, len([q for j, q in enumerate(queries) if j % 20 < 5])):
                print("⏱️  Rate limiting: waiting 1 second...")
                time.sleep(1)
        else:
            print(f"⏭️  Skipping query {i+1}/{total_queries} (batch position {position_in_batch + 1})")
    
    # Save search session
    save_search_session(user_query, total_queries, queries_searched)
    
    print(f"\n📊 Search Summary:")
    print(f"   - Total queries generated: {total_queries}")
    print(f"   - Queries actually searched: {queries_searched}")
    print(f"   - Total results found: {total_results}")
    print(f"   - Results saved to database: {DB_NAME}")
    
    return queries_searched, total_results

def read_prompt_file(filename):
    """Read prompt file content"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filename}")
        return None
    except Exception as e:
        print(f"❌ Error reading {filename}: {str(e)}")
        return None

def call_groq_api(prompt, input_data):
    """Call Groq API with the given prompt and input"""
    # Replace template variables in prompt
    if isinstance(input_data, str):
        full_prompt = prompt.replace('${user_query}', input_data)
    else:
        full_prompt = prompt
        full_prompt = full_prompt.replace('${user_query}', input_data.get('user_query', ''))
        full_prompt = full_prompt.replace('${persona}', input_data.get('persona', ''))
        full_prompt = full_prompt.replace('${company_type}', input_data.get('company_type', ''))
        full_prompt = full_prompt.replace('${location}', input_data.get('location', ''))
        full_prompt = full_prompt.replace('${occupation_description}', input_data.get('occupation_description', ''))
        full_prompt = full_prompt.replace('${company_description}', input_data.get('company_description', ''))
    
    print(f"\n🤖 Calling Groq API...")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}'
    }
    
    payload = {
        'model': 'llama3-8b-8192',
        'messages': [
            {
                'role': 'user',
                'content': full_prompt
            }
        ],
        'temperature': 0.3,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        ai_response = data['choices'][0]['message']['content'].strip()
        
        print(f"✅ AI Response received")
        return ai_response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Groq API: {str(e)}")
        sys.exit(1)
    except KeyError as e:
        print(f"❌ Unexpected API response format: {str(e)}")
        sys.exit(1)

def parse_json_response(response_text, step_name):
    """Parse JSON response from AI, handling potential formatting issues"""
    # Remove markdown code blocks if present
    clean_response = response_text.strip()
    if clean_response.startswith('```json'):
        clean_response = clean_response[7:]
    if clean_response.startswith('```'):
        clean_response = clean_response[3:]
    if clean_response.endswith('```'):
        clean_response = clean_response[:-3]
    
    clean_response = clean_response.strip()
    
    # Look for JSON content between { and }
    start_idx = clean_response.find('{')
    end_idx = clean_response.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_content = clean_response[start_idx:end_idx+1]
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # Look for JSON array content between [ and ]
    start_idx = clean_response.find('[')
    end_idx = clean_response.rfind(']')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_content = clean_response[start_idx:end_idx+1]
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # If all else fails, try the original response
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse {step_name} response as JSON:")
        print(f"Response: {response_text}")
        print(f"Error: {str(e)}")
        sys.exit(1)

def generate_dorked_queries(job_roles, company_names):
    """Generate dorked search queries from job roles and company names"""
    queries = []
    
    for job_role in job_roles:
        for company_name in company_names:
            # Generate single optimized query per combination
            queries.append(f'"intitle:\"{job_role}\" AND (\"{company_name}\" OR \"@{company_name}\" OR \"| {company_name}\" OR \"- {company_name}\" OR \"at {company_name}\" OR \"({company_name})\" OR \": {company_name}\") inurl:/in/"')
            
    return queries

def main():
    """Main function that runs the complete LinkedIn lead research flow"""
    print("🚀 LinkedIn Lead Research Generator")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Get user input
    user_query = input("\n📝 Enter your search query: ").strip()
    if not user_query:
        print("❌ No query provided. Exiting.")
        sys.exit(1)
    
    print(f"\n🔍 Processing: '{user_query}'")
    print("=" * 50)
    
    try:
        # Step 1: Variable Extraction
        print("\n📊 Step 1: Variable Extraction")
        variable_extractor_prompt = read_prompt_file('varible-extractor.md')
        if not variable_extractor_prompt:
            sys.exit(1)
        
        extracted_variables_response = call_groq_api(variable_extractor_prompt, user_query)
        variables = parse_json_response(extracted_variables_response, "variable extraction")
        
        print(f"✅ Extracted Variables:")
        print(f"   - Persona: {variables.get('persona')}")
        print(f"   - Company Type: {variables.get('company_type')}")
        print(f"   - Location: {variables.get('location')}")
        
        # Step 2: Description Generation
        print("\n📝 Step 2: Description Generation")
        description_prompt = read_prompt_file('extracted-variables-to-description.md')
        if not description_prompt:
            sys.exit(1)
        
        descriptions_response = call_groq_api(description_prompt, variables)
        descriptions = parse_json_response(descriptions_response, "description generation")
        
        persona_description = descriptions.get('persona_description')
        company_description = descriptions.get('company_description')
        
        print(f"✅ Persona Description: {persona_description}")
        print(f"✅ Company Description: {company_description}")
        
        # Step 3: Generate Job Roles
        print("\n👥 Step 3A: Generating Job Roles")
        job_roles_prompt = read_prompt_file('job-description-to-role-list.md')
        if not job_roles_prompt:
            sys.exit(1)
        
        job_roles_response = call_groq_api(job_roles_prompt, {'occupation_description': persona_description})
        job_roles = parse_json_response(job_roles_response, "job roles generation")
        
        print(f"✅ Job Roles ({len(job_roles)} found):")
        for i, role in enumerate(job_roles, 1):
            print(f"   {i}. {role}")
        
        # Step 4: Generate Company Names
        print("\n🏢 Step 3B: Generating Company Names")
        company_names_prompt = read_prompt_file('company-description-and-location-to-list.md')
        if not company_names_prompt:
            sys.exit(1)
        
        company_input = {
            'company_description': company_description,
            'location': variables.get('location', '')
        }
        company_names_response = call_groq_api(company_names_prompt, company_input)
        company_names = parse_json_response(company_names_response, "company names generation")
        
        print(f"✅ Company Names ({len(company_names)} found):")
        for i, company in enumerate(company_names, 1):
            print(f"   {i}. {company}")
        
        # Step 5: Generate Dorked Queries
        print("\n🔍 Step 4: Generating Dorked Search Queries")
        dorked_queries = generate_dorked_queries(job_roles, company_names)
        
        print(f"\n🎯 GENERATED DORKED SEARCH QUERIES ({len(dorked_queries)} total):")
        print("=" * 60)
        
        # Show first 10 queries as preview
        for i, query in enumerate(dorked_queries[:10], 1):
            print(f"{i:3d}. {query}")
        
        if len(dorked_queries) > 10:
            print(f"... and {len(dorked_queries) - 10} more queries")
        
        print("\n📊 Query Generation Summary:")
        print(f"   - Job Roles: {len(job_roles)}")
        print(f"   - Company Names: {len(company_names)}")
        print(f"   - Total Queries Generated: {len(dorked_queries)}")
        print(f"   - Combinations: {len(job_roles)} × {len(company_names)} = 1 query per combination")
        
        # Step 6: Search with Exa API (rate limited)
        queries_searched, total_results = search_with_rate_limiting(dorked_queries, user_query)
        
        print("\n✅ LinkedIn lead research completed successfully!")
        print(f"💾 Results saved to database: {DB_NAME}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 