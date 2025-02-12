import tkinter as tk
from tkinter import ttk
import random
from tkinter import messagebox
from markdown_parser import parse_markdown

def load_questions_from_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()[5:] 
        markdown_content = "".join(lines) 
    return parse_markdown(markdown_content)

class AWSQuizApp:
    def __init__(self, root, questions, exam_number):
        self.root = root
        self.root.title("AWS Quiz")
        self.root.geometry("500x400")
        
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")
        
        self.questions = questions
        self.exam_number = exam_number  # Store the exam number
        self.current_question = 0
        self.score = 0
        
        self.question_label = tk.Label(root, text="", wraplength=400, font=("Arial", 12, "bold"))
        self.question_label.pack(pady=20)
        
        self.vars = []  # List to hold the state of each checkbox
        self.options = []  # List to hold the checkboxes
        self.create_option_widgets()  # Create initial checkboxes
        
        self.submit_button = tk.Button(root, text="Submit", command=self.check_answer)
        self.submit_button.pack(pady=10)
        
        self.feedback_label = tk.Label(root, text="", font=("Arial", 10))
        self.feedback_label.pack()
        
        self.next_button = tk.Button(root, text="Next", command=self.next_question, state=tk.DISABLED)
        self.next_button.pack()
        
        self.score_label = tk.Label(root, text=f"Score: {self.score}/{len(self.questions)}", font=("Arial", 10))
        self.score_label.pack()
        
        self.load_question()
    
    def create_option_widgets(self):
        """Create checkboxes for options and center them."""
        self.options_frame = tk.Frame(self.root)
        self.options_frame.pack(pady=10)

        for i in range(5):  # Default number of checkboxes
            var = tk.IntVar(value=0)
            cb = tk.Checkbutton(self.options_frame, text=f"Option {i+1}", variable=var, font=("Arial", 10))
            cb.grid(row=i, column=0, sticky="w", padx=10, pady=2)
            self.vars.append(var)
            self.options.append(cb)
        
    def load_question(self):
        """Load the current question and update the UI."""
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
                cb = tk.Checkbutton(self.root, text=option, variable=var, font=("Arial", 10))
                cb.pack(anchor="w", padx=20)
                self.vars.append(var)
                self.options.append(cb)
        
        for i in range(len(options), len(self.options)):
            self.options[i].config(state=tk.DISABLED, text="")
        
        self.feedback_label.config(text="")
        self.submit_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)
    
    def check_answer(self):
        """Check the selected answers against the correct answers."""
        selected = []
        for i, var in enumerate(self.vars):
            if var.get() == 1:
                option_text = self.question_data["options"][i].strip().lower()
                prefix = option_text.split(".")[0].strip()
                selected.append(prefix)
        
        correct = [ans.strip().lower() for ans in self.question_data["answers"]]
        
        if set(selected) == set(correct):
            self.feedback_label.config(text="Correct!", fg="green")
            self.score += 1
        else:
            self.feedback_label.config(text=f"Incorrect! The correct answers are: {', '.join(correct)}", fg="red")
        
        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        self.score_label.config(text=f"Score: {self.score}/{len(self.questions)}")
        
    def next_question(self):
        """Move to the next question or end the quiz."""
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.load_question()
        else:
            final_score_percent = (self.score / len(self.questions)) * 100
            messagebox.showinfo("Quiz Completed", f"Your final score is {self.score}/{len(self.questions)} ({final_score_percent:.2f}%)")
            self.save_results(final_score_percent)
            
            self.root.destroy()  
            
            root = tk.Tk()
            ExamSelectionApp(root)
            root.mainloop()


    def save_results(self, final_score_percent):
        """Save the exam result in the format [exam-number]#[score] (in percent)."""
        with open("exam_results.txt", "a", encoding="utf-8") as file:
            file.write(f"{self.exam_number}#{final_score_percent:.2f}%\n")

class ExamSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Select AWS Exam")
        
        tk.Label(root, text="Select an exam type (1-23):", font=("Arial", 12)).pack(pady=10)
        
        self.exam_var = tk.StringVar()
        self.exam_dropdown = ttk.Combobox(root, textvariable=self.exam_var, state="readonly")
        self.exam_dropdown['values'] = [f"Exam {i}" for i in range(1, 24)]
        self.exam_dropdown.pack(pady=5)
        
        self.start_button = tk.Button(root, text="Start Quiz", command=self.start_quiz)
        self.start_button.pack(pady=10)
    
    def start_quiz(self):
        """Load selected exam and start the quiz."""
        selected_exam = self.exam_var.get()
        if not selected_exam:
            tk.messagebox.showwarning("Selection Required", "Please select an exam before proceeding.")
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
