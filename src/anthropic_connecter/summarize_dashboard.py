"""Claude-based summarization helpers for Power BI dashboard analysis."""

from __future__ import annotations

import json

import config.config as config
from config.translation import t
from src.anthropic_connecter.general_anthropic_connecter import (
    call_text,
    call_with_image,
)


# ──────────────────────────────────────────────────────────────────────────────
# README flow — per-page summary from JSON + PDF screenshot
# ──────────────────────────────────────────────────────────────────────────────

def summarize_dashboard_by_page_png_json(
    extracted_json_by_page,
    report_images,
    target_platform="Confluence",
    language=config.DEFAULT_LANGUAGE,
    anthropic_client=None,
):
    """For each page, send the JSON and the page screenshot to Claude.

    Returns (full_summary_text, {page_name: page_overview}).
    """
    result_summary = ""
    page_overview_dict: dict[str, str] = {}

    for page_data, page_image in zip(extracted_json_by_page, report_images):
        page_name = page_data["displayName"]
        extracted_json_of_the_page = page_data["extracted_data"]

        system = (
            f"You are an assistant that extracts key information from Power BI "
            f"PBIP report JSON files and screenshots. Respond in {language}."
        )
        user_prompt = (
            "I will provide you with an image and JSON file from a Power BI report. "
            "Retrieve the following information:\n\n"
            "### Instructions\n"
            "1. **Page Overview**\n"
            f"   - Write an overall purpose of the page in {language}.\n\n"
            "2. **Visualizations**\n"
            f"   - List all the visuals on the page, what they represent, and how users can interpret them in {language}.\n\n"
            "3. **Filtering**\n"
            f"   - Explain slicers, filters, or date pickers used on the page in {language}.\n\n"
            "4. **Scenarios for Interpretation**\n"
            "   - Provide examples to guide users on how to interpret the dashboard effectively.\n\n"
            f"### Provided JSON\n{extracted_json_of_the_page}\n\n"
            "### Important Notes\n"
            "- If certain information is not available, omit it without inventing data.\n"
            f"- Structure the output in {language} and format it for {target_platform}.\n\n"
            "### Expected Output Format\n"
            "- Use headings and bullet points.\n"
            f"- Ensure clear and concise explanations in {language} for each section.\n"
        )

        summary = call_with_image(
            anthropic_client,
            system=system,
            user_text=user_prompt,
            image_path=page_image,
        )
        result_summary += f"### {page_name}\n{summary}\n\n"

        structured_prompt = (
            "Extract only the **Page Overview** and **Visualizations** from the "
            "following content and return them as plain text.\n"
            "- Under Visualizations, ignore slicers and focus on charts/tables that "
            "convey meaningful insights.\n\n"
            f"{summary}\n"
        )
        overview = call_text(
            anthropic_client,
            system=f"You are a {language} content extractor specializing in summarizing key sections.",
            user=structured_prompt,
        )
        page_overview_dict[page_name] = overview

    return result_summary, page_overview_dict


# ──────────────────────────────────────────────────────────────────────────────
# README flow — argument synthesis for the add_read_me payload
# ──────────────────────────────────────────────────────────────────────────────

_README_INSTRUCTION = (
    "From the Power BI dashboard overview below, produce a JSON object with this "
    "exact schema:\n"
    "{\n"
    "  \"dashboard_summary\": string,\n"
    "  \"pages\": [\n"
    "    {\n"
    "      \"page_name\": string,\n"
    "      \"page_summary\": string,\n"
    "      \"visuals\": [{\"kpi_name\": string, \"kpi_definition\": string}]\n"
    "    }\n"
    "  ]\n"
    "}\n"
    "Output JSON only — no commentary, no markdown fences."
)


def prepare_readme_arguments(
    overview_all_pages,
    language: str,
    anthropic_client,
) -> dict:
    """Ask Claude to produce a strict JSON document with README content."""
    system = (
        f"You write concise Power BI documentation in {language}. "
        "Return strict JSON only, fully translated into the requested language."
    )
    user = (
        f"{_README_INSTRUCTION}\n\n"
        f"Language for every field: {language}.\n\n"
        f"### Dashboard overview by page\n{overview_all_pages}\n"
    )
    raw = call_text(anthropic_client, system=system, user=user, max_tokens=8192)
    return _parse_json_payload(raw)


def _parse_json_payload(raw: str) -> dict:
    """Parse JSON returned by Claude, tolerant of code fences."""
    if not raw:
        raise ValueError("Empty response from Claude when generating README arguments.")
    text = raw.strip()
    if text.startswith("```"):
        # strip ```json ... ``` fences
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    return json.loads(text)


# ──────────────────────────────────────────────────────────────────────────────
# Documentation flow — JSON-only summaries
# ──────────────────────────────────────────────────────────────────────────────

def global_summary_dashboard(
    extracted_json_by_page,
    target_platform="Confluence",
    language=config.DEFAULT_LANGUAGE,
    anthropic_client=None,
):
    """Single paragraph (~150 words) summarizing the dashboard."""
    system = (
        f"You are a {language} assistant specialized in Power BI dashboards. "
        "Write a concise, comprehensive summary tailored for the requested platform."
    )
    user = (
        f"Create a concise professional summary of a Power BI report in approximately "
        f"150 words in {language} based on the dashboard information below.\n\n"
        f"**Dashboard Information:**\n{extracted_json_by_page}\n\n"
        "### Instructions:\n"
        "- Capture the dashboard's purpose clearly.\n"
        "- Do not invent anything.\n"
        f"- Style the summary for **{target_platform}**.\n"
        f"- Return a single paragraph in {language}, nothing else."
    )
    return call_text(anthropic_client, system=system, user=user)


def summarize_dashboard_by_page(
    extracted_json_by_page,
    target_platform="Confluence",
    language=config.DEFAULT_LANGUAGE,
    anthropic_client=None,
):
    """JSON-only per-page summary (no screenshots)."""
    result_summary = ""
    page_overview_dict: dict[str, str] = {}

    for page_data in extracted_json_by_page:
        page_name = page_data["displayName"]
        extracted_json_of_the_page = page_data["extracted_data"]

        system = (
            f"You are a {language} assistant that extracts key information from "
            "Power BI PBIP report JSON files."
        )
        user = (
            "I will provide you with a JSON file. Retrieve the following:\n\n"
            "### Instructions\n"
            "1. **Page Overview**\n"
            f"   - Overall purpose of the page in {language}.\n\n"
            "2. **Visualizations**\n"
            f"   - List all the visuals on the page and how to interpret them in {language}.\n\n"
            "3. **Filtering**\n"
            f"   - Explain slicers/filters/date pickers in {language}.\n\n"
            "4. **Scenarios for Interpretation**\n"
            "   - Provide interpretation examples.\n\n"
            f"### Provided JSON\n{extracted_json_of_the_page}\n\n"
            "### Important Notes\n"
            "- Omit information not available in the JSON.\n"
            f"- Format the output for {target_platform} and write in {language}.\n"
        )
        summary = call_text(anthropic_client, system=system, user=user)
        result_summary += f"### {page_name}\n{summary}\n\n"

        structured_prompt = (
            "Extract only the **Page Overview** and **Visualizations** from the "
            "following content as plain text. Ignore slicers under Visualizations.\n\n"
            f"{summary}\n"
        )
        page_overview = call_text(
            anthropic_client,
            system=f"You are a {language} content extractor specializing in summarizing key sections.",
            user=structured_prompt,
        )
        page_overview_dict[page_name] = page_overview.strip()

    return result_summary, page_overview_dict


def summarize_table_source(
    table_content,
    target_platform="Confluence",
    language=config.DEFAULT_LANGUAGE,
    anthropic_client=None,
):
    system = (
        f"You are a {language} assistant specialized in extracting Power BI "
        "information from JSON files."
    )
    user = (
        f"Extract and list all table names and their sources from the TABLE "
        f"content below in {language}.\n"
        "- Table names are under each object's 'name' key in 'table_partitions'.\n"
        "- For each table, extract the 'source' key.\n"
        "- If the source has parameters (e.g., 'server_id'), match them to the "
        "'expressions' section to determine their value.\n"
        f"- Describe any dynamic/concatenated value combinations in {language}.\n"
        "- Include all tables; do not omit any.\n"
        "- Do not add introductions, summaries, or irrelevant text.\n"
        f"- Format the result for {target_platform}.\n\n"
        f"### TABLE Content\n{table_content}\n"
    )
    return call_text(anthropic_client, system=system, user=user)


def create_measures_overview_table(
    measures_content,
    target_platform="Confluence",
    language=config.DEFAULT_LANGUAGE,
    anthropic_client=None,
):
    system = (
        f"You are a {language} assistant specialized in summarizing measures in "
        "Power BI dashboards."
    )
    user = (
        "**Create a table** with the following columns:\n"
        f"- {t(language, 'name_measure')}\n"
        f"- {t(language, 'measure_formula')}\n"
        f"- {t(language, 'measure_description')}\n\n"
        "### Instructions\n"
        "1. Measure formulas are under each measure's 'expression' key.\n"
        f"2. Use the exact 'expression' value in the {t(language, 'measure_formula')} column.\n"
        f"3. Include every measure in the {t(language, 'name_measure')} column.\n"
        f"4. Write a short purpose explanation in {language} in the "
        f"{t(language, 'measure_description')} column.\n"
        "5. Return ONLY the table.\n"
        f"6. Format the table for {target_platform}.\n\n"
        "### MEASURES\n"
        f"{measures_content}\n"
    )
    return call_text(anthropic_client, system=system, user=user)


def create_measures_by_column_table(
    measures_content,
    target_platform="Confluence",
    language=config.DEFAULT_LANGUAGE,
    anthropic_client=None,
):
    system = (
        f"You are a {language} assistant specialized in summarizing measures in "
        "Power BI dashboards."
    )
    user = (
        f"**Create a table** with three columns: {t(language, 'name_measure')}, "
        f"{t(language, 'source_table')}, and {t(language, 'used_columns')}, based "
        "on the measures provided below.\n\n"
        "### Instructions\n"
        f"- Each row corresponds to ONE column from the {t(language, 'used_columns')} "
        "of a measure. If a measure uses multiple columns, create separate rows.\n"
        "- Return ONLY the table.\n"
        f"- Format the table for {target_platform}.\n\n"
        "### MEASURES\n"
        f"{measures_content}\n"
    )
    return call_text(anthropic_client, system=system, user=user)
