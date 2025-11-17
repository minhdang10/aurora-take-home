
# Question-Answering System for Member Data
# Main FastAPI application

import json
import httpx
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Member Data QA System", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
MESSAGES_API_URL = "https://november7-730026606190.europe-west1.run.app/messages"


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


class DataFetcher:
    """Fetches and caches member messages data"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self._cache = None
        self._cache_timestamp = None
    
    async def fetch_messages(self, force_refresh: bool = False) -> list:
        """Fetch messages from API with caching"""
        if self._cache is None or force_refresh:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                try:
                    response = await client.get(self.api_url)
                    response.raise_for_status()
                    data = response.json()
                    # API returns {'total': N, 'items': [...]}, extract items
                    if isinstance(data, dict) and 'items' in data:
                        self._cache = data['items']
                    else:
                        self._cache = data if isinstance(data, list) else [data]
                    return self._cache
                except Exception as e:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Failed to fetch messages from API: {str(e)}"
                    )
        return self._cache
    
    def get_messages(self) -> Optional[list]:
        """Get cached messages"""
        return self._cache


data_fetcher = DataFetcher(MESSAGES_API_URL)


async def answer_question(question: str, messages: list) -> str:
    """Answer question using pattern matching"""
    return answer_question_simple(question, messages)


def answer_question_simple(question: str, messages: list) -> str:
    """Simple fallback answer extraction using pattern matching"""
    import re
    question_lower = question.lower()
    
    # Extract person name (capitalized words that might be names)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
    names = re.findall(name_pattern, question)
    # Filter out common words
    common_words = {'When', 'What', 'How', 'Where', 'Who', 'Why', 'The', 'Is', 'Are', 'Does', 'Have', 'Has', 'Her', 'His', 'Their', 'Planning', 'Many', 'Favorite'}
    names = [n for n in names if n not in common_words]
    
    # Look for relevant messages - check user_name field
    relevant_messages = []
    if names:
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            user_name = msg.get('user_name', '').lower()
            message_text = msg.get('message', '').lower()
            # Check if any name matches the user_name or appears in message
            if any(name.lower() in user_name or name.lower() in message_text for name in names):
                relevant_messages.append(msg)
    else:
        relevant_messages = [msg for msg in messages if isinstance(msg, dict)]
    
    name_display = names[0] if names else "the member"
    
    # Trip/London questions
    if "trip" in question_lower or "london" in question_lower:
        for msg in relevant_messages:
            if not isinstance(msg, dict):
                continue
            message_text = msg.get('message', '')
            msg_lower = message_text.lower()
            if "london" in msg_lower:
                # Extract date
                date_patterns = [
                    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                    r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
                    r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',  # Month Day
                    r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # Day of week
                    r'(this|next)\s+(week|friday|monday|tuesday|wednesday|thursday|saturday|sunday)',  # Relative dates
                ]
                dates = []
                for pattern in date_patterns:
                    dates.extend(re.findall(pattern, message_text, re.IGNORECASE))
                if dates:
                    return f"{name_display} is planning a trip to London on {dates[0]}."
                # Check timestamp
                timestamp = msg.get('timestamp', '')
                if timestamp:
                    return f"{name_display} has a trip to London mentioned. Message timestamp: {timestamp[:10]}."
                return f"{name_display} has a trip to London mentioned in their messages."
        return f"I couldn't find information about {name_display}'s trip to London in the data."
    
    # Car questions
    if "car" in question_lower or "cars" in question_lower:
        car_count = 0
        car_mentions = []
        for msg in relevant_messages:
            if not isinstance(msg, dict):
                continue
            message_text = msg.get('message', '')
            msg_lower = message_text.lower()
            if "car" in msg_lower:
                # Try to extract number
                numbers = re.findall(r'\b(\d+)\s*car', msg_lower)
                if numbers:
                    car_count = max(car_count, int(numbers[0]))  # Take the highest number mentioned
                else:
                    car_count += 1
                car_mentions.append(msg)
        if car_count > 0:
            return f"{name_display} has {car_count} car(s) mentioned in the data."
        return f"I couldn't find information about {name_display}'s cars in the data."
    
    # Restaurant questions
    if "restaurant" in question_lower or "favorite" in question_lower:
        restaurants = []
        for msg in relevant_messages:
            if not isinstance(msg, dict):
                continue
            message_text = msg.get('message', '')
            msg_lower = message_text.lower()
            if "restaurant" in msg_lower:
                # Try to extract restaurant names (capitalized words near "restaurant")
                restaurant_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+restaurant'
                found = re.findall(restaurant_pattern, message_text)
                restaurants.extend(found)
                # Also look for quoted names
                quoted = re.findall(r'"([^"]+)"', message_text)
                restaurants.extend([q for q in quoted if "restaurant" in q.lower()])
                # Look for restaurant names in the message
                # Common pattern: "restaurant name" or restaurant name
                restaurant_name_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
                potential_names = re.findall(restaurant_name_pattern, message_text)
                restaurants.extend([n for n in potential_names if len(n.split()) <= 3])
        
        if restaurants:
            unique_restaurants = list(set(restaurants))[:5]  # Limit to 5
            return f"{name_display}'s favorite restaurants include: {', '.join(unique_restaurants)}."
        return f"I couldn't find specific restaurant information for {name_display} in the data."
    
    # Generic fallback
    if relevant_messages:
        return f"I found {len(relevant_messages)} message(s) related to {name_display}, but couldn't extract a specific answer."
    
    return "I don't have enough information to answer that question."


@app.on_event("startup")
async def startup_event():
    #Fetch messages on startup#
    try:
        await data_fetcher.fetch_messages()
    except Exception as e:
        print(f"Could not fetch messages on startup: {e}")


@app.get("/")
async def root():
    #Health check endpoint
    return {
        "status": "ok",
        "service": "Member Data QA System",
        "endpoints": {
            "/ask": "POST - Ask a question about member data",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Fetch messages with cache
    try:
        messages = await data_fetcher.fetch_messages()
        if not messages:
            return AnswerResponse(answer="No member data available at the moment.")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch member data: {str(e)}")
    
    # Answer question
    try:
        answer = await answer_question(request.question, messages)
        return AnswerResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

