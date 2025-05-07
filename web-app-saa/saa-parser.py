import re

def parse_checkbox_markdown(markdown_content):
    """
    Parses checkbox-style markdown questions.
    Returns a list of dictionaries with question, options, and correct answers.
    """
    questions = []
    # Matches question blocks starting with ### and followed by checkbox options
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
