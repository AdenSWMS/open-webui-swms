import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, json
from typing import List, Dict, Any, Optional

# Nutze den auth-helper von Open WebUI, um Anfragen abzusichern
from open_webui.models.users import User
from open_webui.utils.auth import get_verified_user
from sqlalchemy import null 

router = APIRouter()

# Umgebungsvariablen aus Open WebUI laden
LITELLM_URL = os.getenv("LITELLM_URL")
LITELLM_TEAM_ID = os.getenv("LITELLM_TEAM_ID")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")
LITELLM_MAX_BUDGET = os.getenv("LITELLM_MAX_BUDGET", "0.0") 
LITELLM_KEY_DURATION = os.getenv("LITELLM_KEY_DURATION", "30m")  # Standardmäßig 30 Minuten
LITELLM_BUDGET_DURATION = os.getenv("LITELLM_BUDGET_DURATION", "30d")  

openCodeName = "OpenCode"

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

# Modell für die Completion Response
class CompletionResponse(BaseModel):
    model: str
    usage: Usage

# Haupt-Payload für den "after making call" Fall
class SpendCalculateRequest(BaseModel):
    completion_response: CompletionResponse


def get_litellm_provider_header(model_name: str):
    env_mapping = os.getenv("MODEL_MAPPING", "{}")
        
    try:
        model_map = json.loads(env_mapping)
    except json.JSONDecodeError:
        model_map = {}

    current_model = model_name
    
    if current_model in model_map:
        model_with_provider = model_map[current_model]
        
    return model_with_provider


@router.post("/generate-litellm-api-key")
async def generate_litellm_key(user = Depends(get_verified_user)):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "key_alias": f"{openCodeName} {user.name}({user.email})",
        "max_budget": float(LITELLM_MAX_BUDGET),
        "team_id": LITELLM_TEAM_ID,
        "budget_duration": LITELLM_BUDGET_DURATION,
        "duration": LITELLM_KEY_DURATION,
        "user_id": str(user.id)
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LITELLM_URL}/key/generate", 
                json=payload, 
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                if "already exists" in response.text:
                    raise HTTPException(
                        status_code=400, 
                        detail="Ein API-Schlüssel für diesen Benutzer existiert bereit, bitte regenerieren Sie einen neuen Schlüssel."
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"LiteLLM Fehler: {response.text}"
                    )

            return response.json()

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}"
            )


@router.post("/delete-litellm-api-key")
async def delete_litellm_key(user = Depends(get_verified_user)):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "key_aliases": [f"{openCodeName} {user.name}({user.email})"]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LITELLM_URL}/key/delete", 
                json=payload, 
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"LiteLLM Fehler: {response.text}"
                )

            return response.json()

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}"
            ) 
        
@router.post("/spend-for-message")
async def litell_get_spend_for_message(user = Depends(get_verified_user), spend_data: SpendCalculateRequest = None):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    model_with_provider = get_litellm_provider_header(spend_data.completion_response.model)

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "completion_response": {
            "model": model_with_provider,
            "usage": {
                "prompt_tokens": spend_data.completion_response.usage.prompt_tokens,
                "completion_tokens": spend_data.completion_response.usage.completion_tokens,
                "total_tokens": spend_data.completion_response.usage.total_tokens
            }
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LITELLM_URL}/spend/calculate", 
                json=payload, 
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                if "already exists" in response.text:
                    raise HTTPException(
                        status_code=400, 
                        detail="Kosten konnten nicht berechnet werden."
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"LiteLLM Fehler: {response.text}"
                    )

            return response.json()

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}"
            )


async def get_litellm_budget():
    ...

async def get_user_daily_usage():
    ...
