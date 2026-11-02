
from langchain_core.prompts import ChatPromptTemplate
from pipelines.llm_decision import get_decision_llm


def check_passage_relevance(question, passage):
    """
    Evaluate whether a retrieved PDF passage
    contains evidence relevant to the question.
    """

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a document evidence checker.

Return only YES or NO.

YES: The passage explicitly provides information
useful for answering the question.

NO: The passage does not provide useful information.

Use only the passage.
Do not invent missing facts."""
        ),
        (
            "human",
            "Question:\n{question}\n\n"
            "Passage:\n{passage}\n\n"
            "Is this passage relevant?"
        )
    ])

    chain = prompt | get_decision_llm()

    response = chain.invoke({
        "question": question,
        "passage": passage[:1200]
    })

    answer = str(response.content).strip().upper()

    return answer in {"YES", "YES."}
