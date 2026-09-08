from datetime import date
import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import json
from typing import List, Dict, Any, Optional


from open_webui.models.users import User
from open_webui.utils.auth import get_verified_user
from sqlalchemy import null 

router = APIRouter()

LITELLM_URL = os.getenv("LITELLM_URL")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")
LITELLM_MAX_BUDGET = os.getenv("LITELLM_MAX_BUDGET", "0.0") 
LITELLM_KEY_DURATION = os.getenv("LITELLM_KEY_DURATION", "30m") 
LITELLM_BUDGET_DURATION = os.getenv("LITELLM_BUDGET_DURATION", "30d")  

openCodeName = "OpenCode"


async def ensure_litellm_user(user):
  if not LITELLM_MASTER_KEY:
    return {'created': False, 'exists': False, 'error': 'No Master Key'}

  headers = {
      'Authorization': f'Bearer {LITELLM_MASTER_KEY}',
      'Content-Type': 'application/json',
  }

  async with httpx.AsyncClient() as client:
    try:
      check_res = await client.get(
          f'{LITELLM_URL}/user/info',
          params={'user_id': user.email},
          headers=headers,
          timeout=5.0,
      )

      if check_res.status_code == 200:
        return {'created': False, 'exists': True}

      payload = {
          'user_id': user.email,
          'user_alias': f"{user.name} ({user.email})",
          'user_email': user.email,
          'budget_duration': LITELLM_BUDGET_DURATION,
          'max_budget': float(LITELLM_MAX_BUDGET),
          'key_alias': f"{openCodeName} {user.name}({user.email})",
          'duration': LITELLM_KEY_DURATION,
      }

      create_res = await client.post(
          f'{LITELLM_URL}/user/new', json=payload, headers=headers, timeout=10.0
      )

      if create_res.status_code == 200:
        return {'created': True, 'exists': False}

    except Exception as exc:
      print(f'Exception in LiteLLM: {exc}')

  return {'created': False, 'exists': False}


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
        "budget_duration": LITELLM_BUDGET_DURATION,
        "duration": LITELLM_KEY_DURATION,
        "user_id": str(user.email)
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
        
@router.get("/get-user-info")
async def get_user_info(user = Depends(get_verified_user)):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LITELLM_URL}/v2/user/info", 
                params={"user_id": user.email}, 
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
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException

async def get_model_info(model_id: str) -> Optional[Dict[str, Any]]:
    if not LITELLM_MASTER_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LITELLM_URL}/v2/model/info", 
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"LiteLLM Fehler: {response.text}"
                )

            data = response.json().get("data", [])

            for model in data:
                model_name = model.get("model_name")
                litellm_params = model.get("litellm_params", {})

                if model_name == model_id or litellm_params.get("model") == model_id:
                    input_cost = litellm_params.get("input_cost_per_token", 0.0)
                    output_cost = litellm_params.get("output_cost_per_token", 0.0)

                    is_free = (input_cost == 0.0 and output_cost == 0.0)

                    return {
                        "model_name": model_name,
                        "input_cost_per_token": input_cost,
                        "output_cost_per_token": output_cost,
                        "is_free": is_free,
                        "raw_info": model 
                    }

            return None

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}")

#----------------------------------------------------------------
# Budget Analytics Section
#----------------------------------------------------------------

class DailyUsageItem(BaseModel):
    date: str
    spend: float
    tokens: int

class ModelUsageItem(BaseModel):
    model: str
    spend: float
    tokens: int
    calls: int

class ModelTokenDetail(BaseModel):
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class DailyModelDataItem(BaseModel):
    date: str
    model: str
    spend: float

class AnalyticsResponse(BaseModel):
    daily_usage: List[DailyUsageItem]
    model_usage: List[ModelUsageItem]
    model_token_details: List[ModelTokenDetail]
    daily_model_data: List[DailyModelDataItem]

@router.get("/user/analytics", response_model=AnalyticsResponse)
async def get_user_analytics(
    start_date: str = Query(..., description="Startdatum im Format YYYY-MM-DD"),
    end_date: str = Query(..., description="Enddatum im Format YYYY-MM-DD"),
    user = Depends(get_verified_user)
):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "user_id": user.email,
        "start_date": start_date,
        "end_date": end_date
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LITELLM_URL}/user/daily/activity", 
                params=params, 
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"LiteLLM Fehler: {response.text}"
                )

            raw_data = response.json()

            results = raw_data.get("results", []) if isinstance(raw_data, dict) else raw_data

            daily_map = {}
            model_map = {}
            token_map = {}
            daily_model_data = []

            for day in results:
                if not isinstance(day, dict):
                    continue

                entry_date = day.get("date", "")
                day_metrics = day.get("metrics", {})
                
                if entry_date:
                    if entry_date not in daily_map:
                        daily_map[entry_date] = {"spend": 0.0, "tokens": 0}
                        
                    daily_map[entry_date]["spend"] += float(day_metrics.get("spend", 0.0) or 0.0)
                    daily_map[entry_date]["tokens"] += int(day_metrics.get("total_tokens", 0) or 0)

                models_breakdown = day.get("breakdown", {}).get("models", {})
                
                for model_name, model_info in models_breakdown.items():
                    if not isinstance(model_info, dict):
                        continue
                        
                    m_metrics = model_info.get("metrics", {})
                    
                    spend = float(m_metrics.get("spend", 0.0) or 0.0)
                    prompt_tokens = int(m_metrics.get("prompt_tokens", 0) or 0)
                    completion_tokens = int(m_metrics.get("completion_tokens", 0) or 0)
                    total_tokens = int(m_metrics.get("total_tokens", 0) or 0)
                    calls = int(m_metrics.get("api_requests", 0) or 0)

                    if model_name not in model_map:
                        model_map[model_name] = {"spend": 0.0, "tokens": 0, "calls": 0}
                    model_map[model_name]["spend"] += spend
                    model_map[model_name]["tokens"] += total_tokens
                    model_map[model_name]["calls"] += calls

                    if model_name not in token_map:
                        token_map[model_name] = {"prompt": 0, "completion": 0, "total": 0}
                    token_map[model_name]["prompt"] += prompt_tokens
                    token_map[model_name]["completion"] += completion_tokens
                    token_map[model_name]["total"] += total_tokens

                    daily_model_data.append(
                        DailyModelDataItem(date=entry_date, model=model_name, spend=round(spend, 6))
                    )
                    
            return AnalyticsResponse(
                daily_usage=[
                    DailyUsageItem(date=d, spend=round(v["spend"], 4), tokens=int(v["tokens"]))
                    for d, v in daily_map.items()
                ],
                model_usage=[
                    ModelUsageItem(model=m, spend=round(v["spend"], 4), tokens=int(v["tokens"]), calls=int(v["calls"]))
                    for m, v in model_map.items()
                ],
                model_token_details=[
                    ModelTokenDetail(
                        model=m,
                        prompt_tokens=v["prompt"],
                        completion_tokens=v["completion"],
                        total_tokens=v["total"]
                    )
                    for m, v in token_map.items()
                ],
                daily_model_data=daily_model_data
            )

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}"
            )

@router.get("/modelcost")
async def get_model_cost_map(user = Depends(get_verified_user)):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LITELLM_URL}/model/info", 
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"LiteLLM Fehler: {response.text}"
                )

            data = response.json().get("data", [])

            model_cost_map = []
            for model in data:
                model_name = model.get("model_name")
                model_info = model.get("model_info", {})

                input_cost = model_info.get("input_cost_per_token") or 0.0
                output_cost = model_info.get("output_cost_per_token") or 0.0
                cache_read_cost = model_info.get("cache_read_input_token_cost") or 0.0
                cache_write_cost = model_info.get("cache_creation_input_token_cost") or 0.0

                max_input = model_info.get("max_input_tokens") or model_info.get("max_tokens")
                max_output = model_info.get("max_output_tokens") or model_info.get("max_tokens")

                model_cost_map.append({
                    "model": model_name,
                    "input": f"${input_cost * 1_000_000:.2f}" if input_cost else "$0.00",
                    "output": f"${output_cost * 1_000_000:.2f}" if output_cost else "$0.00",
                    "cacheRead": f"${cache_read_cost * 1_000_000:.2f}" if cache_read_cost else "—",
                    "cacheWrite": f"${cache_write_cost * 1_000_000:.2f}" if cache_write_cost else "—",
                    "maxInput": f"{max_input:,}" if max_input else "—",
                    "maxOutput": f"{max_output:,}" if max_output else "—"
                })

            return {"model_cost_map": model_cost_map}

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}"
            )