import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# Nutze den auth-helper von Open WebUI, um Anfragen abzusichern
from open_webui.models.users import User
from open_webui.utils.auth import get_verified_user 

router = APIRouter()

# Umgebungsvariablen aus Open WebUI laden
LITELLM_URL = os.getenv("LITELLM_URL")
LITELLM_TEAM_ID = os.getenv("LITELLM_TEAM_ID")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")
LITELLM_MAX_BUDGET = os.getenv("LITELLM_MAX_BUDGET", "0.0") 
LITELLM_KEY_DURATION = os.getenv("LITELLM_KEY_DURATION", "30m")  # Standardmäßig 30 Minuten
LITELLM_BUDGET_DURATION = os.getenv("LITELLM_BUDGET_DURATION", "30d")  

openCodeName = "OpenCode"


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

async def get_litellm_budget():
    ...

async def get_user_daily_usage():
    ...
