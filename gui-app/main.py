import tkinter as tk
from tkinter import ttk, messagebox
import random
from markdown_parser import parse_markdown
import os

def load_questions_from_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()[5:]
        markdown_content = "".join(lines)
    return parse_markdown(markdown_content)

def load_exam_results():
    """Load exam results and get the highest completion percentage for each exam.
    Ensures all exams from 1 to 23 are included, using '-' for missing scores.
    """
    results = {str(i): 0 for i in range(1, 24)}  # Initialize all exams with '-'
    
    if os.path.exists("exam_results.txt"):
        with open("exam_results.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("#")
                if len(parts) == 2:
                    exam_number, score = parts[0], float(parts[1].replace("%", ""))
                    results[exam_number] = max(results.get(exam_number, 0), score)  # Update max score
    
    return results


class AWSQuizApp:
    def __init__(self, root, questions, exam_number):
        self.root = root
        self.root.title("AWS Quiz")
        self.root.geometry("600x450")
        self.root.configure(bg="#f4f4f4")

        self.questions = questions
        self.exam_number = exam_number  
        self.current_question = 0
        self.score = 0

        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(expand=True, fill="both")

        self.question_label = ttk.Label(self.main_frame, text="", wraplength=550, font=("Arial", 12, "bold"))
        self.question_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.options_frame = ttk.Frame(self.main_frame)
        self.options_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.vars = []  
        self.options = []  
        self.create_option_widgets()

        self.submit_button = ttk.Button(self.main_frame, text="Submit", command=self.check_answer)
        self.submit_button.grid(row=2, column=0, pady=10)

        self.next_button = ttk.Button(self.main_frame, text="Next", command=self.next_question, state=tk.DISABLED)
        self.next_button.grid(row=2, column=1, pady=10)

        self.feedback_label = ttk.Label(self.main_frame, text="", font=("Arial", 10))
        self.feedback_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.score_label = ttk.Label(self.main_frame, text=f"Score: {self.score}/{len(self.questions)}", font=("Arial", 10))
        self.score_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.load_question()

    def create_option_widgets(self):
        for i in range(5):  
            var = tk.IntVar(value=0)
            cb = ttk.Checkbutton(self.options_frame, text=f"Option {i+1}", variable=var)
            cb.grid(row=i, column=0, sticky="w", padx=10, pady=2)
            self.vars.append(var)
            self.options.append(cb)

    def load_question(self):
        self.question_data = self.questions[self.current_question]
        self.question_label.config(text=self.question_data["question"])

        for var in self.vars:
            var.set(0)

        options = self.question_data["options"]
        for i, option in enumerate(options):
            if i < len(self.options):
                self.options[i].config(text=option, state=tk.NORMAL)
            else:
                var = tk.IntVar(value=0)
                cb = ttk.Checkbutton(self.options_frame, text=option, variable=var)
                cb.grid(row=i, column=0, sticky="w", padx=10, pady=2)
                self.vars.append(var)
                self.options.append(cb)

        for i in range(len(options), len(self.options)):
            self.options[i].config(state=tk.DISABLED, text="")

        self.feedback_label.config(text="")
        self.submit_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)

    def check_answer(self):
        selected = [self.question_data["options"][i].strip().lower().split(".")[0] for i, var in enumerate(self.vars) if var.get()]
        correct = [ans.strip().lower() for ans in self.question_data["answers"]]

        if set(selected) == set(correct):
            self.feedback_label.config(text="✅ Correct!", foreground="green")
            self.score += 1
        else:
            self.feedback_label.config(text=f"❌ Incorrect! Correct: {', '.join(correct)}", foreground="red")

        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        self.score_label.config(text=f"Score: {self.score}/{len(self.questions)}")

    def next_question(self):
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.load_question()
        else:
            final_score_percent = (self.score / len(self.questions)) * 100
            messagebox.showinfo("Quiz Completed", f"Your final score: {self.score}/{len(self.questions)} ({final_score_percent:.2f}%)")
            self.save_results(final_score_percent)
            self.root.destroy()
            root = tk.Tk()
            ExamSelectionApp(root)
            root.mainloop()

    def save_results(self, final_score_percent):
        with open("exam_results.txt", "a", encoding="utf-8") as file:
            file.write(f"{self.exam_number}#{final_score_percent:.2f}%\n")

class ExamSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Select AWS Exam")
        self.root.geometry("400x300")
        self.root.configure(bg="#f4f4f4")

        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(expand=True, fill="both")

        ttk.Label(self.main_frame, text="Select an AWS Exam:", font=("Arial", 12)).pack(pady=10)

        self.exam_var = tk.StringVar()
        self.exam_dropdown = ttk.Combobox(self.main_frame, textvariable=self.exam_var, state="readonly", width=25)
        exam_results = load_exam_results()
        self.exam_dropdown["values"] = [f"Exam {num} ({score:.2f}%)" for num, score in exam_results.items()]
        self.exam_dropdown.pack(pady=5)

        self.start_button = ttk.Button(self.main_frame, text="Start Quiz", command=self.start_quiz)
        self.start_button.pack(pady=10)

    def start_quiz(self):
        selected_exam = self.exam_var.get()
        if not selected_exam:
            messagebox.showwarning("Selection Required", "Please select an exam before proceeding.")
            return

        exam_number = selected_exam.split(" ")[1]
        exam_file = f"./cloud_practitioner/practice-exam-{exam_number}.md"

        questions = load_questions_from_markdown(exam_file)
        random.shuffle(questions)

        self.root.destroy()
        root = tk.Tk()
        AWSQuizApp(root, questions, exam_number)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamSelectionApp(root)
    root.mainloop()
