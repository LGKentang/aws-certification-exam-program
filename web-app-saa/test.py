import json
import re
import os
from math import ceil

def parse_checkbox_markdown(markdown_content):
    """
    Parses checkbox-style markdown questions.
    Returns a list of dictionaries with question, options, and correct answers.
    """
    questions = []
    blocks = re.split(r"###\s*", markdown_content)

    for block in blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        question_text = lines[0].strip()
        options = []
        correct_answers = []

        for line in lines[1:]:
            match = re.match(r"- \[( |x)\] (.*)", line.strip())
            if match:
                is_correct = match.group(1).lower() == 'x'
                option_text = match.group(2).strip()
                options.append(option_text)
                if is_correct:
                    correct_answers.append(option_text)

        questions.append({
            "question": question_text,
            "options": options,
            "answers": correct_answers
        })

    return questions


def write_question_batches(questions, batch_size=50, output_dir="."):
    total_batches = ceil(len(questions) / batch_size)
    for i in range(total_batches):
        batch = questions[i * batch_size:(i + 1) * batch_size]
        filename = os.path.join(output_dir, f"saa-question-{i + 1}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            for idx, q in enumerate(batch, start=1 + i * batch_size):
                f.write(f"### {q['question']}\n\n")
                for option in q["options"]:
                    checkbox = "[x]" if option in q["answers"] else "[ ]"
                    f.write(f"- {checkbox} {option}\n")
                f.write("\n\n")


def main():
    filepath = "solution_architect/saa-questions.txt"
    output_dir = "."  # or use "exams/" if you want to store them in a subfolder

    with open(filepath, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    parsed_questions = parse_checkbox_markdown(markdown_content)
    write_question_batches(parsed_questions, batch_size=50, output_dir=output_dir)


if __name__ == "__main__":
    main()
