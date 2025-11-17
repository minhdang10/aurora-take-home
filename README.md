# Member Data Question-Answering System

A simple question-answering system that answers natural-language questions about member data from a public API.

## Features

- **Natural Language Processing**: Answers questions about member data using LLM-based approach
- **RESTful API**: Simple `/ask` endpoint for querying member information
- **Caching**: Efficient data caching to reduce API calls
- **Fallback System**: Works with or without OpenAI API key
- **Data Analysis**: Built-in tools to analyze data for anomalies

## API Endpoint

### POST `/ask`

Ask a natural language question about member data.

**Request:**
```json
{
  "question": "When is Layla planning her trip to London?"
}
```

**Response:**
```json
{
  "answer": "Layla is planning her trip to London on [date from data]"
}
```

### Example Questions

- "When is Layla planning her trip to London?"
- "How many cars does Vikram Desai have?"
- "What are Amira's favorite restaurants?"

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd take-home-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up OpenAI API key for better question-answering:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Testing

Test the API with curl:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
```

Or visit `http://localhost:8000/docs` for interactive API documentation.

## Data Analysis

Run the data analysis script to identify anomalies and inconsistencies:

```bash
python analyze_data.py
```

This will generate a `data_analysis.json` file with detailed findings.

## Deployment

### Railway

1. Create a `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Deploy to Railway:
- Connect your GitHub repository
- Railway will auto-detect Python and install dependencies
- Set `OPENAI_API_KEY` environment variable if using OpenAI

### Render

1. Create a `render.yaml`:
```yaml
services:
  - type: web
    name: member-qa-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
```

2. Deploy to Render and set environment variables

### Fly.io

1. Install flyctl and run:
```bash
fly launch
```

2. Set environment variables:
```bash
fly secrets set OPENAI_API_KEY=your_key_here
```

## Design Notes

### Alternative Approaches Considered

#### 1. **LLM-Based Approach**
**Pros:**
- Handles natural language questions flexibly
- Can understand context and relationships
- Works well with unstructured data
- Easy to extend for new question types

**Cons:**
- Requires API key (costs money)
- Slower response times
- Less deterministic

#### 2. **Rule-Based Pattern Matching**
**Pros:**
- No external dependencies
- Fast and deterministic
- No API costs
- Works offline

**Cons:**
- Requires manual pattern definition for each question type
- Brittle - breaks with slight question variations
- Hard to maintain as question types grow

#### 3. **Vector Database + Semantic Search**
**Pros:**
- Fast retrieval of relevant messages
- Can handle large datasets efficiently
- Good for similarity search

**Cons:**
- Requires embedding model setup
- More complex infrastructure
- Still needs answer generation step

#### 4. **Named Entity Recognition (NER) + Structured Query**
**Pros:**
- Can extract entities (names, dates, locations)
- Structured approach to data extraction
- Good for specific question types

**Cons:**
- Requires training or fine-tuning
- Limited to predefined entity types
- Complex to implement for diverse questions

#### 5. **Hybrid Approach (LLM + Rule-Based Fallback)**
**Pros:**
- Best of both worlds
- Works with or without API key
- Graceful degradation

**Cons:**
- More code to maintain
- Fallback may be less accurate

### Architecture Decisions

1. **FastAPI**: Chosen for async support, automatic OpenAPI docs, and modern Python features
2. **Caching**: Messages are cached to reduce API calls and improve response time
3. **Error Handling**: Graceful fallbacks ensure the system works even if external services fail
4. **Context Window Management**: Limits context size to stay within token limits

## Data Insights

### Analysis Results

Run `python analyze_data.py` to see detailed analysis. Key findings include:

1. **Field Consistency**: Analysis checks for fields that appear inconsistently across messages
2. **Type Variations**: Identifies fields with mixed data types
3. **Missing Data**: Detects empty or null values
4. **Duplicates**: Finds duplicate messages in the dataset

### Common Anomalies Found

- **Inconsistent Field Presence**: Some fields only appear in a subset of messages
- **Type Variations**: Fields may have different types (string vs number) across messages
- **Missing Values**: Some fields may be empty or null
- **Duplicate Entries**: Some messages may be duplicated

See `data_analysis.json` for detailed findings after running the analysis script.

## Project Structure

```
take-home-project/
├── main.py              # FastAPI application
├── analyze_data.py      # Data analysis script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── .env.example        # Environment variable template
``