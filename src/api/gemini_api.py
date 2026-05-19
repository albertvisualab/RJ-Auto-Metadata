# RJ Auto Metadata
# Copyright (C) 2026 Riiicil
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# src/api/gemini_api.py
from __future__ import annotations
import os
import base64
import json
import time
import random
import re
from typing import List, Optional, Union

import openai

from src.api.prompts import select_prompt
from src.utils.logging import log_message
from src.utils.json_utils import _clean_json_text
from src.utils.stop_flag import is_stop_requested

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

API_TIMEOUT = 60
API_MAX_RETRIES = 2
API_RETRY_DELAY = 10
SUCCESS_DELAY = 1.0
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def check_stop_event(stop_event, message=None):
    if is_stop_requested():
        if message: log_message(message)
        return True
    if stop_event is not None:
        try:
            is_set = stop_event.is_set()
            if is_set and message: log_message(message)
            return is_set
        except Exception as e:
            log_message(f"Error checking stop_event: {e}")
            return False
    return False


def _validate_images(image_paths: List[str]):
    for img_path in image_paths:
        _, ext = os.path.splitext(img_path)
        if ext.lower() not in _ALLOWED_EXTENSIONS:
            return False, f"File type {ext.lower()} not supported for API call ({os.path.basename(img_path)})."
    return True, None


def _build_image_content_parts(image_paths: List[str]) -> List[dict]:
    """Build OpenAI-compatible image content parts from file paths."""
    parts: List[dict] = []
    for img_path in image_paths:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        mime = "image/jpeg"
        parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
        })
    return parts


def _extract_metadata_from_text(generated_text: str, keyword_count: Union[str, int]):
    """Parse JSON (or plain-text fallback) into a metadata dict."""
    title = ""
    description = ""
    tags: List[str] = []
    as_category = ""
    ss_category = ""
    try:
        cleaned = _clean_json_text(generated_text)
        try:
            json_data = json.loads(cleaned)
            if isinstance(json_data, dict):
                title = json_data.get("title", "")
                description = json_data.get("description", "")
                keywords = json_data.get("keywords", [])
                if isinstance(keywords, list):
                    tags = [str(kw).strip() for kw in keywords if str(kw).strip()]
                elif isinstance(keywords, str):
                    tags = [kw.strip() for kw in keywords.split(",") if kw.strip()]
                tags = list(dict.fromkeys(tags))[:60]
                as_category = json_data.get("adobe_stock_category", "")
                ss_category = json_data.get("shutterstock_category", "")
                return {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "as_category": as_category,
                    "ss_category": ss_category,
                }
        except (json.JSONDecodeError, TypeError):
            pass
        title_match = re.search(r"^Title:\s*(.*)", generated_text, re.MULTILINE | re.IGNORECASE)
        if title_match: title = title_match.group(1).strip()
        desc_match = re.search(r"^Description:\s*(.*)", generated_text, re.MULTILINE | re.IGNORECASE)
        if desc_match: description = desc_match.group(1).strip()
        keywords_match = re.search(r"^Keywords:\s*(.*)", generated_text, re.MULTILINE | re.IGNORECASE)
        if keywords_match:
            keywords_line = keywords_match.group(1).strip()
            keywords_line = re.split(r"AdobeStockCategory:|ShutterstockCategory:", keywords_line)[0].strip()
            tags = [k.strip() for k in keywords_line.split(",") if k.strip()]
            tags = list(dict.fromkeys(tags))[:60]
        as_cat_match = re.search(r"AdobeStockCategory:\s*([\d]+\.?\s*[^\n]*)", generated_text)
        if as_cat_match:
            as_category = as_cat_match.group(1).strip()
        ss_cat_match = re.search(r"ShutterstockCategory:\s*([^\n]*)", generated_text)
        if ss_cat_match:
            ss_category = ss_cat_match.group(1).strip()
    except Exception as e:
        log_message(f"[ERROR] Failed to parse metadata from Gemini: {e}")
        return None
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "as_category": as_category,
        "ss_category": ss_category,
    }


def get_gemini_metadata(
    image_path,
    api_key,
    stop_event,
    use_png_prompt=False,
    use_video_prompt=False,
    selected_model_input=None,
    keyword_count="49",
    priority="Detailed",
    is_vector_conversion=False,
):
    images: List[str] = image_path if isinstance(image_path, list) else [image_path]
    image_basename = (
        f"{os.path.basename(images[0])} (+{len(images)-1} other frames)"
        if len(images) > 1
        else os.path.basename(images[0])
    )

    is_valid, error_message = _validate_images(images)
    if not is_valid:
        log_message(error_message or "Invalid image for Gemini request", "warning")
        return {"error": error_message or "unsupported_image_format"}

    if check_stop_event(stop_event, f"Gemini request cancelled before submission: {image_basename}"):
        return "stopped"

    model_to_use = (selected_model_input or "gemini-2.0-flash").strip()

    prompt_text = select_prompt(
        priority,
        use_png_prompt=use_png_prompt,
        use_video_prompt=use_video_prompt,
        provider="gemini",
    )

    client = openai.OpenAI(
        api_key=api_key,
        base_url=GEMINI_BASE_URL,
    )

    attempt = 0
    while attempt < API_MAX_RETRIES:
        if check_stop_event(stop_event, f"Gemini attempt {attempt+1} cancelled: {image_basename}"):
            return "stopped"

        log_message(
            f"Sending {image_basename} to Gemini model {model_to_use} via OpenAI compat "
            f"(attempt {attempt+1}/{API_MAX_RETRIES}, key ...{api_key[-5:]})",
            "info",
        )

        try:
            image_parts = _build_image_content_parts(images)
            user_content: List[dict] = image_parts + [{"type": "text", "text": prompt_text}]

            response = client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": user_content}],
                temperature=0.2,
                max_tokens=4096,
                timeout=API_TIMEOUT,
            )

            raw_text = (response.choices[0].message.content or "").strip() if response.choices else ""

            if not raw_text:
                finish = response.choices[0].finish_reason if response.choices else "unknown"
                log_message(
                    f"Gemini returned empty text for {image_basename} (model {model_to_use}, finish={finish})",
                    "warning",
                )
                attempt += 1
                if attempt < API_MAX_RETRIES:
                    _wait_before_retry(attempt, stop_event, image_basename, model_to_use)
                continue

            cleaned = _clean_json_text(raw_text)
            extracted = _extract_metadata_from_text(cleaned, keyword_count)
            if extracted:
                log_message(f"Metadata successfully extracted from {model_to_use} for {image_basename}", "success")
                time.sleep(SUCCESS_DELAY)
                return extracted

            log_message(
                f"Failed to extract metadata structure from Gemini text ({model_to_use}, {image_basename}).",
                "warning",
            )

        except openai.APIStatusError as e:
            status = e.status_code
            msg = str(e.message) if hasattr(e, "message") else str(e)
            if status == 429:
                log_message(f"Rate limit (429) from Gemini for {model_to_use} on {image_basename}: {msg}", "warning")
            elif status in (400, 401, 403):
                log_message(f"Gemini API error (HTTP {status}) for {image_basename}: {msg}. No retry.", "error")
                return {"error": f"{msg} (HTTP {status}, Model {model_to_use})"}
            else:
                log_message(f"Gemini API error (HTTP {status}) for {image_basename}: {msg}", "error")
        except openai.APIConnectionError as e:
            log_message(f"Connection error to Gemini for {image_basename}: {e}", "error")
        except Exception as e:
            log_message(f"Unexpected error calling Gemini for {image_basename}: {e}", "error")

        attempt += 1
        if attempt < API_MAX_RETRIES:
            _wait_before_retry(attempt, stop_event, image_basename, model_to_use)

    final_msg = f"All {API_MAX_RETRIES} attempts failed for {image_basename} (model {model_to_use})."
    log_message(final_msg, "error")
    return {"error": final_msg}


def _wait_before_retry(attempt: int, stop_event, image_basename: str, model: str):
    base_delay = API_RETRY_DELAY * (2 ** (attempt - 1))
    jitter = random.uniform(0, 0.5 * base_delay)
    delay = base_delay + jitter
    log_message(
        f"Waiting {delay:.1f}s before retry {attempt+1}/{API_MAX_RETRIES} "
        f"for {image_basename} (model {model})...",
    )
    start = time.time()
    while time.time() - start < delay:
        if check_stop_event(stop_event, f"Retry delay stopped for {image_basename}"):
            return
        time.sleep(0.1)


def check_api_keys_status(api_keys, model: Optional[str] = None) -> dict:
    results = {}
    test_model = (model or "gemini-2.0-flash").strip()
    for key in api_keys:
        try:
            client = openai.OpenAI(api_key=key, base_url=GEMINI_BASE_URL)
            response = client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Test connectivity. Reply OK."}],
                max_tokens=16,
                timeout=20,
            )
            results[key] = (200, "OK")
        except openai.APIStatusError as e:
            results[key] = (e.status_code, str(e.message) if hasattr(e, "message") else str(e)[:120])
        except Exception as exc:
            results[key] = (-1, str(exc)[:120])
    return results