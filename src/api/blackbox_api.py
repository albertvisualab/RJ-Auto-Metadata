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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# src/api/blackbox_api.py
"""Blackbox AI provider — OpenAI-compatible endpoint."""

import base64
import threading

from openai import OpenAI

from src.api.prompts import select_prompt
from src.utils.json_utils import _clean_json_text
from src.utils.logging import log_message

BASE_URL = "https://api.blackbox.ai"

_force_stop = False
_stop_lock = threading.Lock()


def set_force_stop():
    global _force_stop
    with _stop_lock:
        _force_stop = True


def reset_force_stop():
    global _force_stop
    with _stop_lock:
        _force_stop = False


def is_stop_requested():
    with _stop_lock:
        return _force_stop


def check_stop_event(stop_event, message=None):
    if _force_stop:
        if message:
            log_message(message)
        return True
    if stop_event is not None:
        try:
            if stop_event.is_set():
                if message:
                    log_message(message)
                return True
        except Exception:
            return False
    return False


def select_api_key(api_keys: list) -> str | None:
    return api_keys[0] if api_keys else None


def check_api_keys_status(api_keys: list, model: str = None) -> dict:
    """Check validity of one or more Blackbox API keys."""
    results = {}
    client_model = model or "blackbox"
    for key in api_keys:
        try:
            client = OpenAI(api_key=key, base_url=BASE_URL, timeout=15.0)
            client.chat.completions.create(
                model=client_model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            results[key] = (1, "OK")
        except Exception as e:
            err = str(e)
            if "401" in err or "Unauthorized" in err or "invalid_api_key" in err.lower():
                results[key] = (0, "Invalid API key")
            elif "402" in err or "insufficient" in err.lower():
                results[key] = (0, "Insufficient credits")
            elif "429" in err:
                results[key] = (0, "Rate limited")
            else:
                results[key] = (-1, err[:120])
    return results


def get_blackbox_metadata(
    image_path,
    api_key: str,
    stop_event,
    use_png_prompt: bool = False,
    use_video_prompt: bool = False,
    selected_model_input: str = None,
    keyword_count: str = "49",
    priority: str = "Detailed",
    is_vector_conversion: bool = False,
):
    """Send an image to Blackbox and return parsed metadata dict."""
    if check_stop_event(stop_event, "Blackbox: stop requested before request"):
        return {"error": "stopped"}

    prompt_text = select_prompt(
        priority=priority,
        use_png_prompt=use_png_prompt,
        use_video_prompt=use_video_prompt,
        provider="blackbox",
    )

    model = selected_model_input or "blackbox"

    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Determine MIME type
        path_lower = str(image_path).lower()
        if path_lower.endswith(".png"):
            mime = "image/png"
        elif path_lower.endswith(".gif"):
            mime = "image/gif"
        elif path_lower.endswith(".webp"):
            mime = "image/webp"
        else:
            mime = "image/jpeg"

        client = OpenAI(api_key=api_key, base_url=BASE_URL, timeout=120.0)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{image_data}"
                            },
                        },
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ],
            max_tokens=1024,
        )

        if check_stop_event(stop_event, "Blackbox: stop requested after response"):
            return {"error": "stopped"}

        raw = response.choices[0].message.content or ""
        cleaned = _clean_json_text(raw)

        import json
        metadata = json.loads(cleaned)
        log_message("Metadata successfully extracted from Blackbox response", "success")
        return metadata

    except Exception as e:
        log_message(f"Blackbox request failed: {e}", "error")
        return {"error": str(e)}
