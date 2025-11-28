"""Sidebar components for collecting API key, language, and model."""

import streamlit as st
import config.config as config


def render_sidebar():
    """Render sidebar inputs and return collected values."""
    openai_api_key = st.sidebar.text_input(config.API_KEY_LABEL, type="password")

    language_options = ["English", "French", "Chinese"]
    default_lang_index = (
        language_options.index(config.DEFAULT_LANGUAGE)
        if config.DEFAULT_LANGUAGE in language_options
        else 0
    )
    selected_language = st.sidebar.selectbox(
        "Output language", language_options, index=default_lang_index
    )

    model_options = config.SUPPORTED_MODELS
    default_model_index = (
        model_options.index(config.DEFAULT_MODEL)
        if config.DEFAULT_MODEL in model_options
        else 0
    )
    selected_model = st.sidebar.selectbox(
        "OpenAI model", model_options, index=default_model_index
    )

    return openai_api_key, selected_language, selected_model

