import re

def parse_markdown(markdown_content):
    """
    Parses markdown content and extracts questions, options, and answers.
    Returns a list of dictionaries, each representing a question.
    """
    questions = []
    question_pattern = re.compile(r"(\d+)\.\s*(.*?)\n(.*?)(?=\n\d+\.|\Z)", re.DOTALL)
    option_pattern = re.compile(r"-\s*([A-Z]\.\s*.*)")
    answer_pattern = re.compile(r"Correct answer:\s*([A-Z, ]+)")

    for match in question_pattern.finditer(markdown_content):
        question_text = match.group(2).strip()
        options_text = match.group(3).strip()
        options = [opt.group(1).strip() for opt in option_pattern.finditer(options_text)]
        
        # Find the correct answer(s)
        answer_match = answer_pattern.search(options_text)
        if answer_match:
            correct_answers = [ans.strip() for ans in answer_match.group(1).split(",")]
        else:
            correct_answers = []
        
        questions.append({
            "question": question_text,
            "options": options,
            "answers": correct_answers
        })
    
    return questions
