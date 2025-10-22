import hashlib
import re
import os
import json
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

# --- Pydantic Models ---
class StringProperties(BaseModel):
    """Holds the computed properties of a string."""
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]

class StoredString(BaseModel):
    """The main model for a string stored in our 'database'."""
    id: str = Field(..., description="The SHA-256 hash of the string.")
    value: str
    properties: StringProperties
    created_at: datetime

class CreateStringRequest(BaseModel):
    """The request body for the POST /strings endpoint."""
    value: str = Field(..., min_length=1)

class GetAllStringsResponse(BaseModel):
    """The response for the GET /strings (filtered list) endpoint."""
    data: List[StoredString]
    count: int
    filters_applied: Dict[str, Union[str, int, bool, None]]

class NLPFilterResponse(BaseModel):
    """The response for the GET /strings/filter-by-natural-language endpoint."""
    data: List[StoredString]
    count: int
    interpreted_query: Dict[str, Union[str, Dict[str, Union[str, int, bool]]]]

# --- In-Memory Storage (for Leapcell deployment) ---
# In production, you'd want to use a proper database
stored_strings: Dict[str, StoredString] = {}

# --- Helper Functions ---
def store_string_in_db(stored_string: StoredString):
    """Store a string in memory."""
    stored_strings[stored_string.id] = stored_string

def get_string_from_db(string_value: str) -> Optional[StoredString]:
    """Retrieve a string from memory by its value."""
    sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    return stored_strings.get(sha256_hash)

def delete_string_from_db(string_value: str) -> bool:
    """Delete a string from memory."""
    sha256_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
    if sha256_hash in stored_strings:
        del stored_strings[sha256_hash]
        return True
    return False

def get_all_strings_from_db() -> List[StoredString]:
    """Get all strings from memory."""
    return list(stored_strings.values())

def analyze_string(input_str: str) -> StoredString:
    """Computes all properties for a given string and returns a StoredString object."""
    
    # 1. Length
    length = len(input_str)
    
    # 2. Is Palindrome (case-insensitive)
    normalized_str = input_str.lower()
    is_palindrome = normalized_str == normalized_str[::-1]
    
    # 3. Unique Characters
    unique_characters = len(set(input_str))
    
    # 4. Word Count
    word_count = len(input_str.split())
    
    # 5. SHA-256 Hash
    sha256_hash = hashlib.sha256(input_str.encode('utf-8')).hexdigest()
    
    # 6. Character Frequency Map (case-sensitive, as per Counter's default)
    character_frequency_map = dict(Counter(input_str))
    
    # Build the objects
    properties = StringProperties(
        length=length,
        is_palindrome=is_palindrome,
        unique_characters=unique_characters,
        word_count=word_count,
        sha256_hash=sha256_hash,
        character_frequency_map=character_frequency_map
    )
    
    stored_string = StoredString(
        id=sha256_hash,
        value=input_str,
        properties=properties,
        created_at=datetime.now(timezone.utc)
    )
    
    return stored_string

def _apply_filters_to_list(
    all_strings: List[StoredString],
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None
) -> List[StoredString]:
    """Internal helper function to filter a list of StoredString objects."""
    
    filtered_results = all_strings
    
    if is_palindrome is not None:
        filtered_results = [
            s for s in filtered_results if s.properties.is_palindrome == is_palindrome
        ]
        
    if min_length is not None:
        filtered_results = [
            s for s in filtered_results if s.properties.length >= min_length
        ]

    if max_length is not None:
        filtered_results = [
            s for s in filtered_results if s.properties.length <= max_length
        ]
        
    if word_count is not None:
        filtered_results = [
            s for s in filtered_results if s.properties.word_count == word_count
        ]
        
    if contains_character is not None:
        char_lower = contains_character.lower()
        char_upper = contains_character.upper()
        
        filtered_results = [
            s for s in filtered_results if 
            (char_lower in s.properties.character_frequency_map) or 
            (char_upper in s.properties.character_frequency_map)
        ]
    
    return filtered_results

# --- FastAPI Application ---
app = FastAPI(
    title="String Analyzer Service",
    description="Analyzes strings and stores their computed properties.",
    version="1.0.0"
)

# --- Endpoints ---
@app.post(
    "/strings",
    response_model=StoredString,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze and Store a String"
)
async def create_string(request: CreateStringRequest):
    """Analyzes a new string, computes its properties, and stores it."""
    value = request.value
    
    # Check if string already exists
    existing_string = get_string_from_db(value)
    if existing_string:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists in the system"
        )
        
    analyzed_string = analyze_string(value)
    store_string_in_db(analyzed_string)
    return analyzed_string

@app.get(
    "/strings/{string_value}",
    response_model=StoredString,
    summary="Get a Specific String"
)
async def get_string(string_value: str):
    """Retrieves the analysis data for a specific string value."""
    stored_string = get_string_from_db(string_value)
    if not stored_string:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system"
        )
    return stored_string

@app.delete(
    "/strings/{string_value}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Specific String"
)
async def delete_string(string_value: str):
    """Deletes a specific string from the system."""
    existing_string = get_string_from_db(string_value)
    if not existing_string:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system"
        )
    
    delete_string_from_db(string_value)
    return None

@app.get(
    "/strings",
    response_model=GetAllStringsResponse,
    summary="Get All Strings with Filtering"
)
async def get_all_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None, ge=0),
    max_length: Optional[int] = Query(None, ge=0),
    word_count: Optional[int] = Query(None, ge=1),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1)
):
    """Retrieves a list of all stored strings, with optional filters applied."""
    if min_length is not None and max_length is not None and min_length > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid query parameter values: min_length cannot be greater than max_length"
        )

    filters_applied = {
        "is_palindrome": is_palindrome,
        "min_length": min_length,
        "max_length": max_length,
        "word_count": word_count,
        "contains_character": contains_character
    }
    
    filtered_results = _apply_filters_to_list(
        get_all_strings_from_db(),
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character
    )

    return {
        "data": filtered_results,
        "count": len(filtered_results),
        "filters_applied": {k: v for k, v in filters_applied.items() if v is not None}
    }

@app.get(
    "/strings/filter-by-natural-language",
    response_model=NLPFilterResponse,
    summary="Filter Strings with Natural Language"
)
async def filter_by_nlp(query: str = Query(..., description="The natural language query.")):
    """Parses a simple natural language query to filter strings."""
    original_query = query
    query_lower = query.lower()
    parsed_filters = {}
    
    # Simple Rule-Based NLP
    if "palindromic" in query_lower or "palindrome" in query_lower:
        parsed_filters["is_palindrome"] = True
        
    if "single word" in query_lower or "one word" in query_lower:
        parsed_filters["word_count"] = 1
        
    longer_match = re.search(r"longer than (\d+) characters", query_lower)
    if longer_match:
        parsed_filters["min_length"] = int(longer_match.group(1)) + 1
        
    contains_match = re.search(r"containing the (?:letter|character) (\w)", query_lower)
    if contains_match:
        parsed_filters["contains_character"] = contains_match.group(1).lower()
        
    if "first vowel" in query_lower:
        parsed_filters["contains_character"] = "a"
        
    if "letter z" in query_lower and "contains_character" not in parsed_filters:
        parsed_filters["contains_character"] = "z"
        
    if not parsed_filters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to parse natural language query"
        )
        
    filtered_results = get_all_strings_from_db()
    
    if "is_palindrome" in parsed_filters:
        filtered_results = [s for s in filtered_results if s.properties.is_palindrome]
        
    if "word_count" in parsed_filters:
        target_word_count = parsed_filters["word_count"]
        filtered_results = [s for s in filtered_results if s.properties.word_count == target_word_count]

    if "min_length" in parsed_filters:
        min_len = parsed_filters["min_length"]
        filtered_results = [s for s in filtered_results if s.properties.length >= min_len]
        
    if "contains_character" in parsed_filters:
        char = parsed_filters["contains_character"]
        filtered_results = [s for s in filtered_results if char in s.properties.character_frequency_map]

    return {
        "data": filtered_results,
        "count": len(filtered_results),
        "interpreted_query": {
            "original": original_query,
            "parsed_filters": parsed_filters
        }
    }

@app.get("/", summary="Health Check")
async def root():
    """A simple health check endpoint to confirm the service is running."""
    return {"message": "String Analyzer Service is running on Leapcell!"}

# --- Server Startup ---
# For Leapcell deployment, uvicorn is called directly from leapcell.yaml
# The app instance is exported for uvicorn to use