
import json
import os
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


MODEL_NAME = "qwen2.5:0.5b"



def get_decision_llm():
    """
    Initialize the Qwen model for Windows and Docker.
    """
    return ChatOllama(
        model=MODEL_NAME,
        base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        temperature=0,
        num_ctx=512,
        num_predict=120,
        num_gpu=0,
        num_thread=2
    )


def make_llm_decision(question):
    
    # Reject clearly out-of-scope financial queries
    # before sending the question to the LLM.
    import re

    finance_patterns = [
        r"\bstock\s+price\b",
        r"\bshare\s+price\b",
        r"\bmarket\s+cap(?:italization)?\b",
        r"\bshare\s+market\b",
        r"\bstock\s+market\b",
        r"\b(?:buy|sell)\s+(?:spotify\s+)?(?:shares?|stocks?)\b",
    ]

    if any(
        re.search(pattern, question.lower())
        for pattern in finance_patterns
    ):
        return {
            "scope": "unrelated",
            "intent": "unknown",
            "entities": [],
            "retrieval_mode": "hybrid"
        }

    """
    Classify a user question for Hybrid RAG.

    Returns:
        scope: architecture / unrelated / uncertain
        intent: overview / relationship / detail / unknown
        entities: list of potential component names
        retrieval_mode: hybrid
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """Classify the user's question.

Return ONLY valid JSON:
{{
 "scope": "architecture",
 "intent": "relationship",
 "entities": []
}}

Allowed scope:
architecture, unrelated, uncertain

Allowed intent:
overview, relationship, detail, unknown

Rules:
- Architecture includes software systems,
  components, APIs, services and data flows.
- Unrelated includes sports, weather, recipes,
  and other non-architecture questions.
- Extract component names mentioned in the question.
- Do not invent component names.
- No Markdown or explanations."""
        ),
        ("human", "{question}")
    ])

    chain = prompt | get_decision_llm()

    response = chain.invoke({
        "question": question.strip()
    })

    raw = response.content

    if not isinstance(raw, str):
        raw = ""

    raw = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        raw.strip()
    ).strip()

    # Conservative default: never grant relevance
    # just because the LLM returned malformed JSON.
    decision = {
        "scope": "uncertain",
        "intent": "unknown",
        "entities": [],
        "retrieval_mode": "hybrid"
    }

    try:
        parsed = json.loads(raw)

        if not isinstance(parsed, dict):
            return decision

        allowed_scopes = {
            "architecture", "unrelated", "uncertain"
        }

        allowed_intents = {
            "overview", "relationship",
            "detail", "unknown"
        }

        scope = parsed.get("scope", "uncertain")
        intent = parsed.get("intent", "unknown")
        entities = parsed.get("entities", [])

        if scope in allowed_scopes:
            decision["scope"] = scope

        if intent in allowed_intents:
            decision["intent"] = intent

        if isinstance(entities, list):
            decision["entities"] = [
                entity.strip()
                for entity in entities
                if isinstance(entity, str)
                and entity.strip()
                and entity.lower() in question.lower()
            ]

    except json.JSONDecodeError:
        print(
            "WARNING: LLM returned invalid decision JSON."
        )

    return decision
