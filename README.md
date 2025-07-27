# LinkedIn Lead Research Generator

A comprehensive Python tool that transforms natural language queries into targeted LinkedIn search queries for lead generation. This system uses AI to analyze user input and generate structured, dorked search queries that can be used to find specific professionals on LinkedIn.

## 🚀 Features

- **Natural Language Processing**: Input queries in plain English (e.g., "IT support professionals in top tech firms India")
- **AI-Powered Variable Extraction**: Automatically extracts persona, company type, and location from user queries
- **Smart Description Generation**: Creates comprehensive descriptions that capture broader target audiences
- **Parallel Processing**: Generates both job roles and company lists simultaneously
- **Query Combination Engine**: Creates multiple targeted search combinations
- **Database Storage**: Stores search results and sessions in SQLite database
- **Excel Export**: Export results to formatted Excel files for easy analysis

## 📋 Prerequisites

- Python 3.7 or higher
- [Groq API key](https://console.groq.com/) for AI processing
- [Exa API key](https://exa.ai/) for search functionality

## 🛠 Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd linkedin-lead-research
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (see Configuration section below)

## 📦 Dependencies

The project requires the following Python packages:

- `exa_py` - For Exa search API integration
- `requests` - For HTTP API calls
- `pandas` - For data manipulation and Excel export
- `sqlite3` - For database operations (built-in)
- `json` - For JSON parsing (built-in)
- `datetime` - For timestamp handling (built-in)

## ⚙️ Configuration

### API Keys Setup

You need to configure two API keys in the `linkedin_lead_generator.py` file:

1. **Groq API Key**: Replace `'your_groq_api_key_here'` with your actual Groq API key
   ```python
   GROQ_API_KEY = 'your_actual_groq_api_key'
   ```

2. **Exa API Key**: Replace `'your_exa_api_key_here'` with your actual Exa API key
   ```python
   EXA_API_KEY = 'your_actual_exa_api_key'
   ```

### Getting API Keys

#### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key and replace the placeholder in the code

#### Exa API Key
1. Visit [Exa.ai](https://exa.ai/)
2. Sign up for an account
3. Go to your dashboard/API section
4. Generate an API key
5. Copy the key and replace the placeholder in the code

## 🎯 Usage

### Basic Usage

1. **Run the main script**:
   ```bash
   python linkedin_lead_generator.py
   ```

2. **Enter your search query** when prompted:
   ```
   📝 Enter your search query: IT support professionals in top tech firms India
   ```

3. **The system will process your query through several steps**:
   - Variable extraction (persona, company type, location)
   - Description generation
   - Job roles list generation
   - Company names list generation
   - Query combination and search execution

4. **Results are automatically saved** to the SQLite database

### Export Results to Excel

After running searches, you can export the results:

```bash
python export_to_excel.py
```

This will create an Excel file with timestamp (e.g., `linkedin_leads_export_20240127_143022.xlsx`)

### Example Queries

- "Software engineers at startups in San Francisco"
- "Marketing managers in pharmaceutical companies"
- "Data scientists at Fortune 500 companies in New York"
- "HR professionals in tech companies in Europe"

## 🔄 Process Flow

The system follows this workflow:

1. **User Input**: Natural language query
2. **Variable Extraction**: AI extracts persona, company_type, location
3. **Description Generation**: Creates broader, more inclusive descriptions
4. **Parallel Processing**:
   - Persona → Job Roles List
   - Company Description → Company Names List
5. **Query Combination**: Creates multiple targeted search combinations
6. **Search Execution**: Runs searches using Exa API
7. **Results Storage**: Saves to SQLite database

## 📁 Project Structure

```
manually-generated-prompts/
├── linkedin_lead_generator.py     # Main script
├── export_to_excel.py            # Excel export utility
├── test-file.py                  # API testing script
├── linkedin_leads.db             # SQLite database (auto-created)
├── varible-extractor.md          # AI prompt for variable extraction
├── extracted-variables-to-description.md # AI prompt for description generation
├── job-description-to-role-list.md # AI prompt for job roles generation
├── company-description-and-location-to-list.md # AI prompt for company list generation
├── linkedin-lead-research-flow.md # Detailed process documentation
└── requirements.txt              # Python dependencies
```

## 📊 Database Schema

The system creates two main tables:

### search_results
- `id`: Primary key
- `query`: Search query used
- `title`: Result title
- `url`: LinkedIn profile URL
- `snippet`: Profile snippet/description
- `published_date`: Date information
- `author`: Profile author
- `score`: Relevance score
- `created_at`: Timestamp

### search_sessions
- `id`: Primary key
- `user_query`: Original user input
- `total_queries`: Number of generated queries
- `queries_searched`: Number of queries actually searched
- `created_at`: Session timestamp

## 🔧 Customization

### Modifying AI Prompts

The system uses several markdown files as AI prompts. You can customize these to change behavior:

- `varible-extractor.md`: Modify variable extraction logic
- `extracted-variables-to-description.md`: Adjust description generation
- `job-description-to-role-list.md`: Customize job role generation
- `company-description-and-location-to-list.md`: Modify company list generation

### Adjusting Search Parameters

In `linkedin_lead_generator.py`, you can modify:
- `num_results`: Number of results per query (default: 10)
- Search domains and filtering options
- Rate limiting and retry logic

## 🚨 Important Notes

- **Rate Limits**: Both Groq and Exa APIs have rate limits. The system includes basic rate limiting.
- **API Costs**: Be aware of API usage costs for both services.
- **LinkedIn Terms**: Ensure your usage complies with LinkedIn's Terms of Service.
- **Data Privacy**: Handle personal data responsibly and in compliance with applicable laws.

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure you've replaced placeholder API keys with actual keys
2. **Rate Limiting**: If you hit rate limits, wait before retrying
3. **Database Errors**: Check file permissions in the project directory
4. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`

### Error Messages

- `❌ No query provided`: Enter a non-empty search query
- `❌ API call failed`: Check your API keys and internet connection
- `❌ Database error`: Verify write permissions in project directory

## 📄 License

This project is for educational and research purposes. Please ensure compliance with all applicable terms of service and laws when using this tool for lead generation.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**⚠️ Disclaimer**: This tool is designed for legitimate business lead generation. Users are responsible for ensuring their usage complies with LinkedIn's Terms of Service and applicable privacy laws. 