def system_instructions() -> str:
    return (
        "You are a helpful writing assistant. "
        "Write clearly, cohesively, and at an appropriate level for a general audience. "
        "Avoid repetition and filler. Keep within the requested length."
    )

def subtopic_paragraph_prompt(text: str, subtopic: str, word_count: int) -> str:
    return (
        "Given the following source text:\n\n"
        f"{text}\n\n"
        "Task: Write a cohesive paragraph that fits naturally with the source text.\n"
        f"- Focus subtopic: {subtopic}\n"
        f"- Target length: ~{word_count} words\n"
        "- Ensure coherence with the original tone and content.\n"
        "- Do not repeat the source verbatim; synthesize and expand thoughtfully.\n"
    )

def intro_prompt(main_topic: str, word_count: int) -> str:
    return (
        "Write an engaging introduction that hooks the reader and frames the topic.\n"
        f"- Main topic: {main_topic}\n"
        f"- Target length: ~{word_count} words\n"
        "- Keep it clear, informative, and inviting; avoid clichés.\n"
    )

def get_subtopic_prompt(main_topic: str, num: int) -> str:
    """
    Instruct the model to return strict JSON with a 'subtopics' array.
    """
    return (
        "You must reply ONLY with valid JSON (no markdown, no prose).\n"
        "Schema:\n"
        "{\n"
        '  "subtopics": [string, ...]\n'
        "}\n\n"
        f"Generate {num} focused, non-overlapping subtopics for the main topic:\n"
        f"\"{main_topic}\".\n"
        "- Be specific; avoid duplicates and trivial variants.\n"
        "- Keep each subtopic short (max ~8 words).\n"
    )
