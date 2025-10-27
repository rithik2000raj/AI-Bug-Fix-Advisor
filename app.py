import gradio as gr
import time
import os
from config import Config
from error_parser import ErrorParser
from groq_handler import GroqBugFixer
from utils.formatters import OutputFormatter

# Validate configuration on startup
try:
    Config.validate_config()
    print("✅ Configuration validated successfully!")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)

# Initialize components
error_parser = ErrorParser()
groq_fixer = GroqBugFixer()
formatter = OutputFormatter()


def analyze_code(code, error_traceback):
    """Main function to analyze code and generate fixes"""
    if not code or not code.strip():
        return "❌ Please provide Python code to analyze."

    if not error_traceback or not error_traceback.strip():
        return "❌ Please provide the error traceback."

    try:
        # Show loading state
        yield "Analyzing your code and error... Please wait."
        time.sleep(1)

        # Step 1: Parse and analyse error
        analysis = error_parser.analyze_error(code, error_traceback)

        yield f"Generating three different solutions..."
        time.sleep(0.5)

        # Step 2: Generate fixes using Groq
        result = groq_fixer.generate_fixes(code, error_traceback, analysis)

        # Step 3: Format final output
        final_output = formatter.format_final_output(result)

        yield final_output

    except Exception as e:
        error_message = f"❌ An error occurred during analysis:\n{str(e)}"
        yield error_message


# Create Gradio interface
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
    ),
    title="AI Bug Fix Advisor 🐞",
    css="""
    .gradio-container {
        max-width: 1400px !important;
        margin: 0 auto;
    }
    .input-box textarea {
        border-radius: 10px;
        font-family: 'Monaco', 'Consolas', monospace;
        color: #000000 !important;
        background: #ffffff !important;
    }
    .output-box {
        border-radius: 10px;
        font-family: 'Monaco', 'Consolas', monospace;
        background: #f8f9fa !important;
        color: #000000 !important;
    }
    .output-box .markdown {
        color: #000000 !important;
    }
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }
    .header:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(102, 126, 234, 0.25);
    }
    .feature-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .feature-card h4 {
        color: #000000 !important;
    }
    .feature-card p {
        color: #333333 !important;
    }
    .thick-separator {
        height: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        margin: 40px 0;
        border-radius: 3px;
        border: none;
    }
    .permanent-separator {
        height: 8px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        margin: 30px 0;
        border-radius: 4px;
        border: none;
        width: 100%;
    }
    .markdown {
        color: #000000 !important;
    }
    .markdown p, .markdown h1, .markdown h2, .markdown h3, .markdown h4, .markdown h5, .markdown h6 {
        color: #000000 !important;
    }
    .tab-item {
        color: #000000 !important;
    }
    .label {
        color: #000000 !important;
    }
    textarea {
        color: #000000 !important;
        background: #ffffff !important;
    }
    .prose {
        color: #000000 !important;
    }
    .solution-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 25px;
        margin-top: 20px;
        text-align: center;
    }
    .solution-card {
        background: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 2px solid #667eea;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        color: #000000;
        width: 320px;
        max-width: 90%;
    }
    .solution-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 18px rgba(102, 126, 234, 0.25);
    }
    .analyze-button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    }
    @media (min-width: 900px) {
        .solution-card:nth-child(3) {
            flex-basis: 60%;
        }
    }
    .solution-card h4 {
        color: #000000;
        margin-bottom: 10px;
        font-weight: 700;
    }
    .solution-card p {
        color: #333333;
        margin: 0;
    }

    """,
) as demo:

    # Header Section
    with gr.Row():
        with gr.Column():
            gr.HTML(
                """
            <div class="header">
                <h1 style="color: white; margin: 0;">🐞 AI Bug Fix Advisor</h1>
                <p style="font-size: 1.2em; margin-bottom: 0; color: white;">Smart Python Debugging Assistant • Three Solutions for Every Bug</p>

            </div>
            """
            )

    # Main Content
    with gr.Row(equal_height=True):
        # Input Column
        with gr.Column(scale=1, min_width=500):
            gr.Markdown("### Input Your Code & Error")

            with gr.Tabs():
                with gr.TabItem("Code Input"):
                    code_input = gr.Textbox(
                        label="Python Code",
                        placeholder="""# Paste your Python code here
def example_function():
    numbers = []
    average = sum(numbers) / len(numbers)
    return average

result = example_function()""",
                        lines=15,
                        show_copy_button=True,
                    )

                with gr.TabItem("Error Input"):
                    error_input = gr.Textbox(
                        label="Error Traceback",
                        placeholder="""# Paste the complete error traceback here
Traceback (most recent call last):
  File "example.py", line 6, in <module>
    result = example_function()
  File "example.py", line 3, in example_function
    average = sum(numbers) / len(numbers)
ZeroDivisionError: division by zero""",
                        lines=10,
                        show_copy_button=True,
                    )

            # Quick Examples
            with gr.Accordion("Quick Examples", open=False):
                with gr.Row():
                    example1_btn = gr.Button("File Processing", size="sm")
                    example2_btn = gr.Button("API Data Handling", size="sm")
                    example3_btn = gr.Button("Database Operations", size="sm")

            # Analyze Button
            analyze_btn = gr.Button(
                "🔍 Analyze & Generate Fixes",
                variant="primary",
                size="lg",
                scale=1,
                elem_classes="analyze-button",
            )

        # Output Column
        with gr.Column(scale=1, min_width=500):

            output = gr.Markdown(
                label="Three Solution Approaches",
                value="""
## Welcome!

Paste your Python code on the **left tab** and error traceback on the **right tab**, then click the **"Analyze & Generate Fixes"** button to get three different solutions for your bug!

""",
            )

    # Permanent separator line
    gr.HTML("""<div class="permanent-separator"></div>""")

    # Features Section
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Solution Approaches")
            gr.HTML(
                """
    <div class="solution-grid">
        <div class="solution-card">
            <h4>Solution 1: Simple Fix</h4>
            <p>Direct, beginner-friendly correction that solves the immediate problem.</p>
        </div>

        <div class="solution-card">
            <h4>Solution 2: Try-Except Handling</h4>
            <p>Professional error handling with proper exception management.</p>
        </div>

        <div class="solution-card">
            <h4>Solution 3: Alternative Approach</h4>
            <p>Creative different implementation or best practice solution.</p>
        </div>
    </div>
    """
            )

    # Example data
    example_1_code = """def process_user_data(filename):
    with open(filename, 'r') as file:
        data = file.read()
    
    users = data.split('\\n')
    for user in users:
        name, age = user.split(',')
        print(f"Name: {name}, Age: {age}")

# This will cause multiple potential errors
process_user_data('users.txt')"""

    example_1_error = """Traceback (most recent call last):
  File "example.py", line 9, in <module>
    process_user_data('users.txt')
  File "example.py", line 2, in process_user_data
    with open(filename, 'r') as file:
FileNotFoundError: [Errno 2] No such file or directory: 'users.txt'"""

    example_2_code = """import requests

def get_user_data(user_id):
    response = requests.get(f'https://api.example.com/users/{user_id}')
    user_data = response.json()
    return user_data['data']['email']

# Multiple potential issues
email = get_user_data(123)
print(f"User email: {email}")"""

    example_2_error = """Traceback (most recent call last):
  File "example.py", line 8, in <module>
    email = get_user_data(123)
  File "example.py", line 4, in get_user_data
    user_data = response.json()
  File "requests/models.py", line 900, in json
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)"""

    example_3_code = """def calculate_discount(price, discount_percent):
    discounted_price = price * (1 - discount_percent / 100)
    final_price = discounted_price + (discounted_price * 0.18)  # 18% tax
    return final_price

# Multiple calculation and type issues
prices = [100, 200, "300", 400]
for price in prices:
    final = calculate_discount(price, 20)
    print(f"Final price: {final}")"""

    example_3_error = """Traceback (most recent call last):
  File "example.py", line 9, in <module>
    final = calculate_discount(price, 20)
  File "example.py", line 2, in calculate_discount
    discounted_price = price * (1 - discount_percent / 100)
TypeError: unsupported operand type(s) for *: 'str' and 'float'"""

    # Connect the main button
    analyze_btn.click(fn=analyze_code, inputs=[code_input, error_input], outputs=output)

    # Connect example buttons
    example1_btn.click(
        fn=lambda: [example_1_code, example_1_error], outputs=[code_input, error_input]
    )

    example2_btn.click(
        fn=lambda: [example_2_code, example_2_error], outputs=[code_input, error_input]
    )

    example3_btn.click(
        fn=lambda: [example_3_code, example_3_error], outputs=[code_input, error_input]
    )

if __name__ == "__main__":
    print("🚀 Starting AI Bug Fix Advisor...")
    print(f"📊 Using model: {Config.MODEL_NAME}")
    print("🌐 Server starting...")
    print("📍 Open the URL below to access the application:")
    print("   http://localhost:7860")
    print("\n💡 Tips:")
    print("   - Make sure your GROQ_API_KEY is set in the .env file")
    print("   - Try the example buttons to quickly test the system")
    print("   - Each analysis provides three different solution approaches")

    try:
        demo.launch(
            share=False,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            show_api=False,
            quiet=False,
            inbrowser=True,
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Try changing the port: python app.py --port 7861")
