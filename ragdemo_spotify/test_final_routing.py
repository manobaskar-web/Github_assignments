
from pipelines.answer_generator import generate_grounded_answer

tests = [
    {
        "name": "General architecture relationships",
        "question": "How do the major components communicate with each other?",
        "expected": "supported"
    },
    {
        "name": "Specific service relationships",
        "question": "How does Media Processor Service interact with other services?",
        "expected": "supported"
    },
    {
        "name": "Unrelated sports question",
        "question": "Who won the FIFA World Cup in 2022?",
        "expected": "refused"
    },
    {
        "name": "Unrelated financial question",
        "question": "What is Spotify's current stock price?",
        "expected": "refused"
    },
    {
        "name": "Unrelated relationship wording",
        "question": "How do football teams communicate with each other?",
        "expected": "refused"
    }
]

passed = 0

for index, test in enumerate(tests, start=1):

    print("\n" + "=" * 65)
    print("TEST:", index, "-", test["name"])
    print("QUESTION:", test["question"])

    try:
        result = generate_grounded_answer(
            test["question"]
        )

        supported = result.get("supported", False)
        pages = result.get("pages", [])
        answer = result.get("answer", "")

        actual = (
            "supported" if supported else "refused"
        )

        status = (
            "PASS" if actual == test["expected"]
            else "FAIL"
        )

        print("EXPECTED:", test["expected"])
        print("ACTUAL:", actual)
        print("RESULT:", status)
        print("PDF PAGES:", pages)
        print("ANSWER:", answer)

        if status == "PASS":
            passed += 1

    except Exception as error:
        print(
            "RESULT: ERROR",
            type(error).__name__,
            str(error)
        )

print("\n" + "=" * 65)
print(f"TOTAL PASSED: {passed}/{len(tests)}")
