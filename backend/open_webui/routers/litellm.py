from datetime import date
import math
import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Query
from open_webui.utils.litellm_session_managment.session_manager import session_manager
from pydantic import BaseModel
import json
from typing import List, Dict, Any, Optional
import re


from open_webui.internal.db import get_async_db_context, get_async_session
from open_webui.models.users import User
from open_webui.utils.auth import get_admin_user, get_verified_user
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

LITELLM_URL = os.getenv("LITELLM_URL")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")
LITELLM_MAX_BUDGET = os.getenv("LITELLM_MAX_BUDGET", "0.0") 
LITELLM_KEY_DURATION = os.getenv("LITELLM_KEY_DURATION", "30m") 
LITELLM_BUDGET_DURATION = os.getenv("LITELLM_BUDGET_DURATION", "30d")  

openCodeName = "OpenCode"
BUDGET_INCREASE_AMOUNT = float(os.getenv("LITELLM_BUDGET_INCREASE_AMOUNT", "5.0"))
MAX_BUDGET_INCREASE_COUNT = int(os.getenv("LITELLM_MAX_BUDGET_INCREASE_COUNT", "3"))


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

@router.post("/update-user-budget")
async def update_user_budget(
    new_budget: float = Query(..., description="Neues Budget für den Benutzer"),
    user_to_update: str = Query(..., description="E-Mail des Benutzers, dessen Budget aktualisiert werden soll"),
    user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_async_session),
):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(status_code=500, detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert.")
    if not math.isfinite(new_budget) or new_budget < 0:
        raise HTTPException(status_code=422, detail='Das Budget muss eine endliche, nicht negative Zahl sein.')

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with db.begin():
            await db.execute(
                update(User)
                .where(User.email == user_to_update.lower())
                .values(budget_base=new_budget, budget_increase_count=0)
            )
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{LITELLM_URL}/user/update",
                    json={"user_id": user_to_update, "max_budget": new_budget},
                    headers=headers,
                    timeout=10.0,
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"LiteLLM Fehler: {response.text}",
                    )
                return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"LiteLLM Server nicht erreichbar: {exc}") from exc


@router.post('/increase-user-budget')
async def increase_own_user_budget(
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(status_code=500, detail='LITELLM_MASTER_KEY ist nicht konfiguriert.')

    headers = {
        'Authorization': f'Bearer {LITELLM_MASTER_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        async with db.begin():
            claimed = await db.execute(
                update(User)
                .where(User.id == user.id, User.budget_increase_count < MAX_BUDGET_INCREASE_COUNT)
                .values(budget_increase_count=User.budget_increase_count + 1)
            )
            if claimed.rowcount != 1:
                raise HTTPException(status_code=409, detail='Alle drei Budgeterhöhungen wurden bereits verwendet.')

            async with httpx.AsyncClient() as client:
                info_response = await client.get(
                    f'{LITELLM_URL}/v2/user/info',
                    params={'user_id': user.email},
                    headers=headers,
                    timeout=10.0,
                )
                if info_response.status_code != 200:
                    raise HTTPException(status_code=502, detail='Das Budget konnte nicht geprüft werden.')

                info = info_response.json()
                try:
                    spend = float(info['spend'])
                    max_budget = float(info['max_budget'])
                except (KeyError, TypeError, ValueError) as exc:
                    raise HTTPException(status_code=502, detail='Das Budget konnte nicht geprüft werden.') from exc

                if not math.isfinite(spend) or not math.isfinite(max_budget) or max_budget <= 0 or spend < max_budget:
                    raise HTTPException(status_code=409, detail='Das Budget muss vollständig verbraucht sein.')

                new_budget = max_budget + BUDGET_INCREASE_AMOUNT
                update_response = await client.post(
                    f'{LITELLM_URL}/user/update',
                    json={'user_id': user.email, 'max_budget': new_budget},
                    headers=headers,
                    timeout=10.0,
                )
                if update_response.status_code != 200:
                    raise HTTPException(status_code=502, detail='Das Budget konnte nicht erhöht werden.')

            count = await db.scalar(select(User.budget_increase_count).where(User.id == user.id))
            return {'max_budget': new_budget, 'budget_increase_count': count}
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail='LiteLLM Server nicht erreichbar.') from exc


async def _fetch_litellm_user_info(user_email: str) -> dict:
    if not LITELLM_MASTER_KEY:
        raise HTTPException(status_code=500, detail='LITELLM_MASTER_KEY ist nicht konfiguriert.')

    headers = {
        'Authorization': f'Bearer {LITELLM_MASTER_KEY}',
        'Content-Type': 'application/json',
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{LITELLM_URL}/v2/user/info',
                params={'user_id': user_email},
                headers=headers,
                timeout=10.0,
            )
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail='LiteLLM Nutzerbudget konnte nicht geladen werden.')
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail='LiteLLM Server nicht erreichbar.') from exc


async def _reconcile_user_budget_period(user, user_info: dict) -> dict:
    info = dict(user_info)
    reset_at = info.get('budget_reset_at')
    refresh_info = False

    try:
        current_budget = float(info['max_budget'])
        if not math.isfinite(current_budget):
            current_budget = None
    except (KeyError, TypeError, ValueError):
        current_budget = None

    async with get_async_db_context() as session:
        async with session.begin():
            row = (
                await session.execute(
                    select(User.budget_base, User.budget_increase_count, User.budget_period_reset_at).where(
                        User.id == user.id
                    )
                )
            ).first()
            if row is None:
                info.update(budget_base=None, budget_period_reset_at=None, budget_increase_count=0)
                return info

            base_budget, increase_count, last_reset_at = row
            increase_count = int(increase_count or 0)

            if not isinstance(reset_at, str) or not reset_at or current_budget is None:
                pass
            elif last_reset_at == reset_at:
                if base_budget is None:
                    base_budget = max(0.0, current_budget - BUDGET_INCREASE_AMOUNT * increase_count)
                    await session.execute(
                        update(User).where(User.id == user.id).values(budget_base=base_budget)
                    )
            elif last_reset_at is None:
                if base_budget is None:
                    base_budget = max(0.0, current_budget - BUDGET_INCREASE_AMOUNT * increase_count)
                await session.execute(
                    update(User)
                    .where(User.id == user.id, User.budget_period_reset_at.is_(None))
                    .values(budget_base=base_budget, budget_period_reset_at=reset_at)
                )
            else:
                claimed = await session.execute(
                    update(User)
                    .where(User.id == user.id, User.budget_period_reset_at == last_reset_at)
                    .values(budget_period_reset_at=reset_at)
                )
                if claimed.rowcount == 1:
                    if base_budget is None:
                        base_budget = max(0.0, current_budget - BUDGET_INCREASE_AMOUNT * increase_count)

                        headers = {
                            'Authorization': f'Bearer {LITELLM_MASTER_KEY}',
                            'Content-Type': 'application/json',
                        }
                        try:
                            async with httpx.AsyncClient() as client:
                                response = await client.post(
                                    f'{LITELLM_URL}/user/update',
                                    json={'user_id': user.email, 'max_budget': base_budget},
                                    headers=headers,
                                    timeout=10.0,
                                )
                                if response.status_code != 200:
                                    raise HTTPException(status_code=502, detail='LiteLLM Budget konnte nicht zurückgesetzt werden.')
                        except httpx.RequestError as exc:
                            raise HTTPException(status_code=503, detail='LiteLLM Server nicht erreichbar.') from exc

                        await session.execute(
                            update(User)
                            .where(User.id == user.id)
                            .values(budget_base=base_budget, budget_increase_count=0)
                        )
                    refresh_info = True
                else:
                    refresh_info = True

    if refresh_info:
        info = await _fetch_litellm_user_info(user.email)

    async with get_async_db_context() as session:
        budget_state = await session.execute(
            select(User.budget_base, User.budget_period_reset_at, User.budget_increase_count).where(
                User.id == user.id
            )
        )
        row = budget_state.one_or_none()

    if row is None:
        info.update(budget_base=None, budget_period_reset_at=None, budget_increase_count=0)
    else:
        info.update(
            budget_base=row.budget_base,
            budget_period_reset_at=row.budget_period_reset_at,
            budget_increase_count=row.budget_increase_count,
        )
    return info



@router.get("/get-user-info")
async def get_user_info(user = Depends(get_verified_user)):
    return await _reconcile_user_budget_period(user, await _fetch_litellm_user_info(user.email))

@router.get("/get-all-users-info")
async def get_all_users_info(user = Depends(get_admin_user)):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500, 
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert."
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }

    all_users = []
    page = 1
    page_size = 100

    async with httpx.AsyncClient() as client:
        try:
            while True:
                response = await client.get(
                    f"{LITELLM_URL}/user/list", 
                    headers=headers,
                    params={"page": page, "page_size": page_size},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"LiteLLM Fehler: {response.text}"
                    )

                data = response.json()
                users_page = data.get("users", [])
                all_users.extend(users_page)

                total_pages = data.get("total_pages", 1)
                if page >= total_pages or not users_page:
                    break
                
                page += 1

            return {
                "users": all_users,
                "total": len(all_users),
                "page": 1,
                "page_size": len(all_users),
                "total_pages": 1
            }

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


UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


@router.get("/user/analytics", response_model=AnalyticsResponse)
async def get_user_analytics(
    start_date: str = Query(..., description="Startdatum im Format YYYY-MM-DD"),
    end_date: str = Query(..., description="Enddatum im Format YYYY-MM-DD"),
    user=Depends(get_verified_user),
):
    if not LITELLM_MASTER_KEY:
        raise HTTPException(
            status_code=500,
            detail="LITELLM_MASTER_KEY ist im Open WebUI Backend nicht konfiguriert.",
        )

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json",
    }

    params = {
        "user_id": user.email,
        "start_date": start_date,
        "end_date": end_date,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LITELLM_URL}/user/daily/activity",
                params=params,
                headers=headers,
                timeout=10.0,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LiteLLM Fehler: {response.text}",
                )

            raw_data = response.json()

            results = (
                raw_data.get("results", [])
                if isinstance(raw_data, dict)
                else raw_data
            )

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

                    daily_map[entry_date]["spend"] += float(
                        day_metrics.get("spend", 0.0) or 0.0
                    )
                    daily_map[entry_date]["tokens"] += int(
                        day_metrics.get("total_tokens", 0) or 0
                    )

                models_breakdown = (
                    day.get("breakdown", {}).get("models", {})
                )

                for model_name, model_info in models_breakdown.items():
                    if not isinstance(model_info, dict):
                        continue

                    # Filter: UUIDs überspringen
                    if UUID_PATTERN.match(model_name):
                        continue

                    m_metrics = model_info.get("metrics", {})

                    spend = float(m_metrics.get("spend", 0.0) or 0.0)
                    prompt_tokens = int(
                        m_metrics.get("prompt_tokens", 0) or 0
                    )
                    completion_tokens = int(
                        m_metrics.get("completion_tokens", 0) or 0
                    )
                    total_tokens = int(
                        m_metrics.get("total_tokens", 0) or 0
                    )
                    calls = int(m_metrics.get("api_requests", 0) or 0)

                    if model_name not in model_map:
                        model_map[model_name] = {
                            "spend": 0.0,
                            "tokens": 0,
                            "calls": 0,
                        }
                    model_map[model_name]["spend"] += spend
                    model_map[model_name]["tokens"] += total_tokens
                    model_map[model_name]["calls"] += calls

                    if model_name not in token_map:
                        token_map[model_name] = {
                            "prompt": 0,
                            "completion": 0,
                            "total": 0,
                        }
                    token_map[model_name]["prompt"] += prompt_tokens
                    token_map[model_name]["completion"] += completion_tokens
                    token_map[model_name]["total"] += total_tokens

                    daily_model_data.append(
                        DailyModelDataItem(
                            date=entry_date,
                            model=model_name,
                            spend=round(spend, 6),
                        )
                    )

            return AnalyticsResponse(
                daily_usage=[
                    DailyUsageItem(
                        date=d,
                        spend=round(v["spend"], 4),
                        tokens=int(v["tokens"]),
                    )
                    for d, v in daily_map.items()
                ],
                model_usage=[
                    ModelUsageItem(
                        model=m,
                        spend=round(v["spend"], 4),
                        tokens=int(v["tokens"]),
                        calls=int(v["calls"]),
                    )
                    for m, v in model_map.items()
                ],
                model_token_details=[
                    ModelTokenDetail(
                        model=m,
                        prompt_tokens=v["prompt"],
                        completion_tokens=v["completion"],
                        total_tokens=v["total"],
                    )
                    for m, v in token_map.items()
                ],
                daily_model_data=daily_model_data,
            )

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"LiteLLM Server nicht erreichbar: {exc}",
            )

@router.get("/model_info")
async def get_model_info_map(user = Depends(get_verified_user)):
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

            model_info_map = []
            for model in data:
                model_name = model.get("model_name")
                model_info = model.get("model_info", {})
                litellm_params = model.get("litellm_params", {})

                input_cost = model_info.get("input_cost_per_token") or 0.0
                output_cost = model_info.get("output_cost_per_token") or 0.0
                cache_read_cost = model_info.get("cache_read_input_token_cost") or 0.0
                cache_write_cost = model_info.get("cache_creation_input_token_cost") or 0.0

                max_input = model_info.get("max_input_tokens") or model_info.get("max_tokens")
                max_output = model_info.get("max_output_tokens") or model_info.get("max_tokens")

                model_info_map.append({
                    "model": model_name,
                    "provider": model_info.get("litellm_provider") or litellm_params.get("litellm_provider"),
                    "description": model_info.get("description") or model.get("description"),
                    "supports_vision": bool(model_info.get("supports_vision", model.get("supports_vision", False))),
                    "supports_reasoning": bool(model_info.get("supports_reasoning", model.get("supports_reasoning", False))),
                    "supports_function_calling": bool(model_info.get("supports_function_calling", model.get("supports_function_calling", False))),
                    "input": f"${input_cost * 1_000_000:.2f}" if input_cost else "$0.00",
                    "output": f"${output_cost * 1_000_000:.2f}" if output_cost else "$0.00",
                    "cacheRead": f"${cache_read_cost * 1_000_000:.2f}" if cache_read_cost else "—",
                    "cacheWrite": f"${cache_write_cost * 1_000_000:.2f}" if cache_write_cost else "—",
                    "maxInput": f"{max_input:,}" if max_input else "—",
                    "maxOutput": f"{max_output:,}" if max_output else "—",
                })

            return {"model_info_map": model_info_map}

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"LiteLLM Server nicht erreichbar: {exc}"
            )

######################################
# Session Management with Redis
######################################
class CreateSessionRequest(BaseModel):
    max_budget: float
    user_email: Optional[str] = None  # Optional: Nur Admins geben hier eine abweichende Mail an
    ttl_seconds: Optional[int] = None  # z.B. 86400 für 24 Stunden



@router.post("/create-session")
async def create_session(
    req: CreateSessionRequest, 
    user=Depends(get_verified_user)
):
    """
    Erstellt oder überschreibt eine Session.
    Nimmt standardmäßig die E-Mail des eingewählten Users.
    """
    target_email = user.email

    # Wenn eine abweichende E-Mail angegeben wurde, Rechte prüfen (z. B. Admin-Check)
    if req.user_email and req.user_email != user.email:
        if getattr(user, "role", None) != "admin":
            raise HTTPException(
                status_code=403, 
                detail="Nur Admins dürfen Sessions für andere Nutzer erstellen."
            )
        target_email = req.user_email

    session = session_manager.create_or_update_session(
        user_email=target_email,
        max_budget=req.max_budget,
        ttl_seconds=req.ttl_seconds
    )
    return {"status": "success", "session": session}


@router.get("/get-session")
async def get_my_session(user=Depends(get_verified_user)):
    """Liest den aktuellen Session-Stand (Spend / Budget) des eingewählten Nutzers aus."""
    session = session_manager.get_session(user.email)
    if not session:
        return {
            "status": "none", 
            "message": f"Keine aktive Session für {user.email} gefunden.",
            "session": None
        }
    return {"status": "success", "session": session}


@router.delete("/delete-session")
async def delete_my_session(user=Depends(get_verified_user)):
    """Löscht die Session des eingewählten Nutzers aus Redis."""
    deleted = session_manager.delete_session(user.email)
    if not deleted:
        raise HTTPException(
            status_code=404, 
            detail=f"Keine aktive Session für {user.email} vorhanden."
        )
    return {"status": "success", "message": f"Session für {user.email} gelöscht."}


@router.delete("/user/{target_email}")
async def delete_user_session(
    target_email: str, 
    user=Depends(get_admin_user)
):
    """Admin-Endpunkt: Löscht die Session eines beliebigen Nutzers."""
    if getattr(user, "role", None) != "admin" and target_email != user.email:
        raise HTTPException(status_code=403, detail="Keine Berechtigung.")

    deleted = session_manager.delete_session(target_email)
    if not deleted:
        raise HTTPException(
            status_code=404, 
            detail=f"Session für {target_email} existiert nicht."
        )
    return {"status": "success", "message": f"Session für {target_email} gelöscht."}