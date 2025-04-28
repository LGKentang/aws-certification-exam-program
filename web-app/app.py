from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import random
import os
import re

app = Flask(__name__)
app.secret_key = 'jjjjjjlkjljkljljjjjjjkjljljlkjkljljkkjjlkjlkjkjlkj'

def load_questions_from_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()[5:]
        markdown_content = "".join(lines)
    return parse_markdown(markdown_content)

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

def load_exam_results():
    """Load exam results and get the highest completion percentage for each exam."""
    results = {str(i): 0 for i in range(1, 24)}  # Initialize all exams with '-'
    
    if os.path.exists("exam_results.txt"):
        with open("exam_results.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("#")
                if len(parts) == 2:
                    exam_number, score = parts[0], float(parts[1].replace("%", ""))
                    results[exam_number] = max(results.get(exam_number, 0), score)  # Update max score
    
    return results


@app.route('/')
def index():
    exam_results = load_exam_results()
    print(exam_results)
    exams = [f"Exam {num} ({score:.2f}%)" for num, score in exam_results.items()]
    return render_template('index.html', exams=exams)

@app.route('/quiz/<exam_number>', methods=['GET', 'POST'])
def quiz(exam_number):
    exam_file = f"./cloud_practitioner/practice-exam-{exam_number}.md"
    questions = load_questions_from_markdown(exam_file)

    current_question = int(request.args.get('current_question', 0))
    score = int(request.cookies.get('score', 0))
    feedback = None

    if request.method == 'POST':
        selected_answers = request.form.getlist(f'question_{current_question}')
        correct_answers = questions[current_question]["answers"]

        if set(selected_answers) == set(correct_answers):
            feedback = "Correct!"
            score += 1
        else:
            feedback = f"Incorrect. Correct answer(s): {', '.join(correct_answers)}"

        # Stay on same question, but set feedback
        resp = render_template('quiz.html',
                                questions=questions,
                                exam_number=exam_number,
                                feedback=feedback,
                                current_question=current_question,
                                selected_answers=selected_answers,
                                total_questions=len(questions),
                                progress_percent=(current_question + 1) / len(questions) * 100)
        response = app.make_response(resp)
        response.set_cookie('score', str(score))
        return response

    # Quiz Completed
    if current_question >= len(questions):
        final_score_percent = (score / len(questions)) * 100

        # Save results
        save_results(exam_number, final_score_percent)

        resp = render_template('quiz_complete.html',
                                final_score=final_score_percent,
                                correct_answers=score,
                                total_questions=len(questions),
                                exam_number=exam_number)
        response = app.make_response(resp)
        response.delete_cookie('score')
        return response

    return render_template('quiz.html',
                            questions=questions,
                            exam_number=exam_number,
                            feedback=feedback,
                            current_question=current_question,
                            selected_answers=[],
                            total_questions=len(questions),
                            progress_percent=(current_question + 1) / len(questions) * 100)


# Save results to a file
def save_results(exam_number, final_score_percent):
    with open("exam_results.txt", "a", encoding="utf-8") as file:
        file.write(f"{exam_number}#{final_score_percent:.2f}%\n")

if __name__ == '__main__':
    app.run(debug=True)
