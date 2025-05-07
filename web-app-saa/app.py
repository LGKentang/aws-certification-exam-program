from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import random
import os
import re

app = Flask(__name__)
app.secret_key = 'jjjjjjlkjljkljljjjjjjkjljljlkjkljljkkjjlkjlkjkjlkj'

def load_questions_from_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        markdown_content = "".join(lines)
    return parse_markdown(markdown_content)

def parse_markdown(markdown_content):
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
                    correct_answers.append(option_text.rstrip('.').strip())

        
        questions.append({
            "question": question_text,
            "options": options,
            "answers": correct_answers
        })
    print(questions[0])

    return questions


def load_exam_results():
    """Load exam results and get the highest completion percentage and name for each exam."""
    results = {str(i): {"score": 0, "name": "-"} for i in range(1, 15)}

    if os.path.exists("exam_results.txt"):
        with open("exam_results.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("#")
                if len(parts) == 3:
                    exam_number = parts[0]
                    score = float(parts[1].replace("%", ""))
                    name = parts[2].strip()
                    if score > results[exam_number]["score"]:
                        results[exam_number] = {"score": score, "name": name}

    return results


def load_exam_results_2():
    """Load exam results and get the highest completion percentage and name for each exam."""
    results = {str(i): [] for i in range(1, 15)}  # Create an empty list for each exam number

    if os.path.exists("exam_results.txt"):
        with open("exam_results.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("#")
                if len(parts) == 3:
                    exam_number = parts[0]
                    score = float(parts[1].replace("%", ""))  # Remove the '%' and convert to float
                    name = parts[2].strip()

                    # Append the result as a tuple (score, name) to the respective exam number
                    results[exam_number].append((score, name))

    # Sort results for each exam by score in descending order
    for exam_number, result_list in results.items():
        results[exam_number] = sorted(result_list, reverse=True, key=lambda x: x[0])  # Sort by score

    return results

@app.route('/')
def index():
    exam_results = load_exam_results()
    # print(exam_results)
    exams = [
        f"Exam {num} ({data['score']:.2f}% - {data['name']})"
        for num, data in exam_results.items()
    ]
    return render_template('index.html', exams=exams)

@app.route('/leaderboard/<exam_number>')
def leaderboard(exam_number):
    exam_results = load_exam_results_2()
    # print(exam_results)
    

    # Get the sorted results for the specific exam
    if exam_number in exam_results:
        results = exam_results[exam_number]
    else:
        results = []
    
    unique_results = list(dict.fromkeys(results))  # Preserves order

    # Optional: sort by score descending
    unique_results.sort(reverse=True)

    return render_template('leaderboard.html', exam_number=exam_number, results=unique_results)

@app.route('/quiz/<exam_number>', methods=['GET', 'POST'])
def quiz(exam_number):
    exam_file = f"./solution_architect/saa-question-{exam_number}.txt"
    questions = load_questions_from_markdown(exam_file)

    current_question = int(request.args.get('current_question', 0))
    score = session.get('score', 0)
    feedback = None


    # Start of quiz: reset score
    if current_question == 0:
        session['score'] = 0
        score = 0

    # Quiz completed
    if current_question >= len(questions):
        final_score_percent = (score / len(questions)) * 100

        # Handle name submission
        if request.method == 'POST' and 'user_name' in request.form:
            user_name = request.form['user_name']
            save_results(exam_number, final_score_percent, user_name)
            session.pop('score', None)
            return redirect(url_for('index'))

        # Show name input form
        return render_template('enter_name.html',
                               final_score=final_score_percent,
                               correct_answers=score,
                               total_questions=len(questions),
                               exam_number=exam_number)

    # Handle answer submission
    if request.method == 'POST':
        selected_answers = request.form.getlist(f'question_{current_question}')
        correct_answers = questions[current_question]["answers"]
        

        if set(selected_answers) == set(correct_answers):
            feedback = "Correct!"
            score += 1
        else:
            feedback = f"Incorrect. Correct answer(s): {', '.join(correct_answers)}"

        session['score'] = score

    return render_template('quiz.html',
                           questions=questions,
                           exam_number=exam_number,
                           feedback=feedback,
                           current_question=current_question,
                           selected_answers=request.form.getlist(f'question_{current_question}') if request.method == 'POST' else [],
                           total_questions=len(questions),
                           progress_percent=(current_question + 1) / len(questions) * 100)



def save_results(exam_number, final_score_percent, user_name):
    with open("exam_results.txt", "a", encoding="utf-8") as file:
        file.write(f"{exam_number}#{final_score_percent:.2f}%#{user_name.strip()}\n")


if __name__ == '__main__':
    app.run(debug=True)
