import os
import time
import requests
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Models tried in order — fast first, more powerful as fallback
MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]

# Direct REST API models for image / table pipelines (no LangChain overhead)
DIRECT_MODELS    = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
_DIRECT_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent"
)
_DIRECT_MAX_RETRIES = 2
_DIRECT_RETRY_DELAY = 8   # seconds — pause on 503 overload before retry

# Smallest model used only for key validation (minimal quota cost)
_VALIDATION_MODEL = "gemini-2.0-flash"

# Keywords that indicate a quota / rate-limit error
_QUOTA_KEYWORDS = [
    "quota", "resource_exhausted", "resourceexhausted", "429",
    "rate limit", "limit exceeded", "ratequotaexceeded",
    "userratequotaexceeded", "too many requests",
]


# ── Exception ─────────────────────────────────────────────────────────────────

class AllKeysExhausted(Exception):
    """Raised when every API key in the pool has hit its quota."""
    def __init__(self, available: list, exhausted: list):
        self.available = available   # always []
        self.exhausted = exhausted
        super().__init__(
            f"All {len(exhausted)} API key(s) exhausted. Please provide a new key."
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_quota_error(error):

    error_text = str(error).lower()

    for word in _QUOTA_KEYWORDS:

        if word in error_text:
            return True

    return False


def _make_llm(model, api_key, temperature=0.3, max_output_tokens=4096):
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        google_api_key=api_key,
    )


def invoke_with_fallback(state, prompt, variables):
    available = list(state.get("available_api_keys") or [])
    exhausted = list(state.get("exhausted_api_keys") or [])
    last_error = None

    for api_key in list(available):  
        for model_name in MODELS:
            try:
                resp = (prompt | _make_llm(model_name, api_key)).invoke(variables)
                return resp.content, {
                    "available_api_keys": available,
                    "exhausted_api_keys": exhausted,
                }
            except Exception as exc:
                last_error = exc
                if _is_quota_error(exc):
                    available.remove(api_key)
                    exhausted.append(api_key)
                    break           # key is dead — move on to the next one
                # non-quota error: try next model with the same key

    if not available:
        raise AllKeysExhausted(available, exhausted)
    raise last_error or RuntimeError("LLM invocation failed across all models.")


# ── Direct REST fallback (image / table pipelines) ───────────────────────────

def gemini_direct_call(available_keys, exhausted_keys, parts,
                       temperature=0.2, max_tokens=350):
    """
    Direct REST API version of invoke_with_fallback for pipelines that cannot
    use LangChain (image extraction, table extraction).

    Tries every key in available_keys × every model in DIRECT_MODELS with up
    to _DIRECT_MAX_RETRIES attempts on transient overload errors (503).

    On quota / rate-limit errors (429 or matching _QUOTA_KEYWORDS) the key is
    moved from available to exhausted and the next key is tried.

    Returns (response_text, updated_available_keys, updated_exhausted_keys).
    Raises AllKeysExhausted when every key has been exhausted.
    """
    # Filter out blank keys up-front
    available = [k for k in available_keys if k and k.strip()]
    exhausted = list(exhausted_keys)

    if not available:
        raise AllKeysExhausted(available, exhausted)

    for api_key in list(available):
        key_dead = False
        for model in DIRECT_MODELS:
            if key_dead:
                break
            for attempt in range(1, _DIRECT_MAX_RETRIES + 1):
                url     = _DIRECT_BASE_URL.format(model=model) + f"?key={api_key}"
                payload = {
                    "contents": [{"parts": parts}],
                    "generationConfig": {
                        "temperature":     temperature,
                        "maxOutputTokens": max_tokens,
                    },
                }
                try:
                    resp = requests.post(url, json=payload, timeout=60)

                    if resp.status_code == 200:
                        text = (
                            resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        )
                        return text, available, exhausted

                    if resp.status_code == 404:
                        break   # model not found → skip to next model

                    # Quota / rate-limit → key is dead
                    if resp.status_code == 429 or _is_quota_error(resp.text):
                        if api_key in available:
                            available.remove(api_key)
                            exhausted.append(api_key)
                        key_dead = True
                        break

                    # Transient overload → retry same model
                    if resp.status_code == 503 and attempt < _DIRECT_MAX_RETRIES:
                        time.sleep(_DIRECT_RETRY_DELAY)
                        continue

                    # Any other HTTP error or final 503 → try next model
                    break

                except Exception as exc:
                    if _is_quota_error(exc):
                        if api_key in available:
                            available.remove(api_key)
                            exhausted.append(api_key)
                        key_dead = True
                        break
                    # Network / timeout error → try next model
                    break

    raise AllKeysExhausted([], exhausted)


# ── Key validation ────────────────────────────────────────────────────────────

def validate_api_key(api_key):

    api_key = api_key.strip()

    if not api_key:
        return False, "Key is empty"

    try:

        llm = _make_llm(
            "gemini-2.0-flash",
            api_key,
            temperature=0,
            max_output_tokens=5
        )

        llm.invoke("Reply with ok")

        return True, "Key is valid"

    except Exception as e:

        if _is_quota_error(e):
            return False, "Key quota exhausted"

        return False, str(e)



def save_api_key_to_env(api_key, env_path=None):
    """Save a new key to os.environ and append it to the .env file."""
    api_key = api_key.strip()
    existing = sum(1 for k in os.environ if k.startswith("GEMINI_API_KEY_"))
    key_name = f"GOOGLE_API_KEY_{existing + 1}"
    os.environ[key_name] = api_key

    if env_path is None:
        env_path = Path(__file__).parent.parent / ".env"
    try:
        with open(env_path, "a") as fh:
            fh.write(f"\n{key_name}={api_key}\n")
    except OSError:
        pass   # .env not writable — os.environ update is still in effect

    return key_name
