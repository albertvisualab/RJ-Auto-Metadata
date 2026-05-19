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

# src/api/prompts.py
import threading

_prompt_overrides = threading.local()


def _set_prompt_overrides(config: dict) -> None:
    """Set thread-local prompt overrides (called from process_single_file)."""
    _prompt_overrides.config = config or {}


def _clear_prompt_overrides() -> None:
    """Clear thread-local prompt overrides after processing completes."""
    _prompt_overrides.config = {}


_ADOBE_STOCK_CATEGORY_LIST = (
    "1.Animals, 2.Architecture, 3.Business, 4.Drinks, 5.Environment, 6.Mind, 7.Food, 8.Graphics, 9.Leisure, 10.Industry, 11.Landscapes, 12.Lifestyle, 13.People, 14.Plants, 15.Religion, 16.Science, 17.Social, 18.Sports, 19.Technology, 20.Transport, 21.Travel"
)

_SHUTTERSTOCK_CATEGORY_LIST_IMAGE = (
    "'Abstract', 'Animals/Wildlife', 'Arts', 'Backgrounds/Textures', 'Beauty/Fashion', 'Buildings/Landmarks', 'Business/Finance', 'Education', 'Food and drink', 'Healthcare/Medical', 'Industrial', 'Nature', 'Objects', 'People', 'Religion', 'Science', 'Signs/Symbols', 'Sports/Recreaction', 'Technology', 'Transportation'"
)

_SHUTTERSTOCK_CATEGORY_LIST_VIDEO = (
    "'Animals/Wildlife', 'Arts', 'Backgrounds/Textures', 'Buildings/Landmarks', 'Business/Finance', 'Education', 'Food and drink', 'Healthcare/Medical', 'Holidays', 'Industrial', 'Nature', 'Objects', 'People', 'Religion', 'Science', 'Signs/Symbols', 'Sports/Recreaction', 'Technology', 'Transportation'"
)

_OPENAI_JSON_TEMPLATE = '{"title": "", "description": "", "keywords": [], "adobe_stock_category": "", "shutterstock_category": ""}'

_PRIORITY_PARAMS = {
    "Detailed": {"min_words": 6, "max_chars": 180},
    "Balanced": {"min_words": 5, "max_chars": 165},
    "Fast": {"min_words": 4, "max_chars": 150},
}


def _build_gemini_prompt(
    min_words: int,
    max_chars: int,
    is_png: bool = False,
    is_video: bool = False,
    user_hint: str = "",
    custom_instruction: str = "",
) -> str:
    """Build Gemini-style prompt (inline JSON schema format)."""
    if is_video:
        intro = "Analyze these video frames comprehensively and generate detailed JSON video metadata:"
        title_rule = f"video title, minimum {min_words} words, max {max_chars} chars, unique, dont use special characters"
        desc_rule = f"video description, max {max_chars} chars, unique, dont use special characters"
        shutterstock = _SHUTTERSTOCK_CATEGORY_LIST_VIDEO
    elif is_png:
        intro = "Analyze main subject only (ignore background), generate JSON:"
        title_rule = f"focused on main subject, minimum {min_words} words, max {max_chars} chars, unique, dont use special characters"
        desc_rule = f"focused on main subject details only, max {max_chars} chars, unique, dont use special characters"
        shutterstock = _SHUTTERSTOCK_CATEGORY_LIST_IMAGE
    else:
        intro = "Analyze image, generate JSON metadata:"
        title_rule = f"minimum {min_words} words, max {max_chars} chars, descriptive, unique, dont use special characters"
        desc_rule = f"detailed, max {max_chars} chars, unique, dont use special characters"
        shutterstock = _SHUTTERSTOCK_CATEGORY_LIST_IMAGE

    hint_block = f"\nUser context: {user_hint.strip()}" if user_hint.strip() else ""
    custom_block = f"\nAdditional instructions: {custom_instruction.strip()}" if custom_instruction.strip() else ""

    return (
        f"{intro}{hint_block}\n"
        '{"title": ["' + title_rule + '"], '
        '"description": ["' + desc_rule + '"], '
        '"keywords": ["Give me 60 unique keywords, ensure at least 55 unique; '
        'if fewer are obvious, add closely-related synonyms/variations. No multi-word phrases. Array"], '
        '"adobe_stock_category": ["pick number and name: ' + _ADOBE_STOCK_CATEGORY_LIST + '"], '
        '"shutterstock_category": ["pick: ' + shutterstock + '"]}'
        + custom_block
    )


def _build_openai_prompt(
    min_words: int,
    max_chars: int,
    is_png: bool = False,
    is_video: bool = False,
    user_hint: str = "",
    custom_instruction: str = "",
) -> str:
    """Build OpenAI-style prompt (structured English + JSON template)."""
    if is_video:
        intro = "Analyze all video frames comprehensively and generate detailed video metadata."
        shutterstock = _SHUTTERSTOCK_CATEGORY_LIST_VIDEO
    elif is_png:
        intro = "Focus ONLY on the main subject of the image (ignore the transparent or plain background)."
        shutterstock = _SHUTTERSTOCK_CATEGORY_LIST_IMAGE
    else:
        intro = "Analyze the entire image and produce production-ready metadata."
        shutterstock = _SHUTTERSTOCK_CATEGORY_LIST_IMAGE

    hint_block = f"\nUser context: {user_hint.strip()}" if user_hint.strip() else ""

    # If user instructions are present, add an explicit note that the char limit
    # applies to the TOTAL final output (including any additions).
    char_note = ""
    if user_hint.strip() or custom_instruction.strip():
        char_note = (
            f" The TOTAL final title (including any prefix or suffix from user instructions) "
            f"must not exceed {max_chars} characters. Shorten the descriptive portion if needed."
        )

    custom_block = (
        f"\nAdditional user instructions (prioritize these, but keep JSON schema intact): "
        f"{custom_instruction.strip()}"
        if custom_instruction.strip() else ""
    )

    return (
        f"You are a stock photography metadata generator. {intro}{hint_block}\n\n"
        "Output requirements:\n"
        f"- Title: Minimum {min_words} words, maximum {max_chars} characters, "
        f"descriptive, unique, no special characters.{char_note}\n"
        f"- Description: Minimum {min_words} words, maximum {max_chars} characters, "
        "detailed, unique, no special characters.\n"
        "- Keywords: Provide up to 60 unique keywords; ensure at least 55 unique. "
        "If fewer are obvious, add closely-related synonyms/variations. No multi-word phrases.\n"
        f"- Adobe Stock category: choose the number and name from: {_ADOBE_STOCK_CATEGORY_LIST}.\n"
        f"- Shutterstock category: choose one from: {shutterstock}.\n"
        f"{custom_block}\n"
        "Return ONLY valid JSON matching this schema exactly "
        "(no extra text, comments, or markdown):\n"
        f"{_OPENAI_JSON_TEMPLATE}"
    )


def select_prompt(
    priority: str,
    use_png_prompt: bool = False,
    use_video_prompt: bool = False,
    provider: str = "openai",
    user_hint: str = "",
    custom_instruction: str = "",
    min_words_override: int = 0,
    max_chars_override: int = 0,
) -> str:
    """Select and build the correct prompt for the given provider and context.

    This is the single public entry point for all *_api.py modules.
    The signature is backward-compatible: existing callers that do not pass
    user_hint or custom_instruction receive identical prompt text as before.

    min_words_override and max_chars_override: when > 0, override the preset
    values from _PRIORITY_PARAMS. Use these to support user-defined quality limits.

    Thread-local overrides (set via _set_prompt_overrides) are applied when the
    corresponding explicit parameter is at its default value, allowing the
    processing pipeline to inject Advanced tab values without modifying every
    intermediate caller.
    """
    if priority == "Less":
        priority = "Fast"

    # Merge thread-local overrides for params left at their defaults
    _ovr = getattr(_prompt_overrides, "config", {})
    if not user_hint:
        user_hint = _ovr.get("user_hint", "")
    if not custom_instruction:
        custom_instruction = _ovr.get("custom_instruction", "")
    if min_words_override <= 0:
        min_words_override = _ovr.get("title_min_words", 0)
    if max_chars_override <= 0:
        max_chars_override = _ovr.get("title_max_chars", 0)

    params = _PRIORITY_PARAMS.get(priority, _PRIORITY_PARAMS["Detailed"])
    min_words = min_words_override if min_words_override > 0 else params["min_words"]
    max_chars = max_chars_override if max_chars_override > 0 else params["max_chars"]

    provider_key = (provider or "openai").strip().lower()

    if provider_key == "gemini":
        return _build_gemini_prompt(
            min_words=min_words,
            max_chars=max_chars,
            is_png=use_png_prompt,
            is_video=use_video_prompt,
            user_hint=user_hint,
            custom_instruction=custom_instruction,
        )
    else:
        return _build_openai_prompt(
            min_words=min_words,
            max_chars=max_chars,
            is_png=use_png_prompt,
            is_video=use_video_prompt,
            user_hint=user_hint,
            custom_instruction=custom_instruction,
        )
