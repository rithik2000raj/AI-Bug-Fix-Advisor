import groq
from config import Config
from utils.formatters import OutputFormatter
import subprocess
import tempfile
import os


class GroqBugFixer:
    def __init__(self):
        self.client = groq.Client(api_key=Config.GROQ_API_KEY)
        self.model = Config.MODEL_NAME
        self.formatter = OutputFormatter()

    def generate_fixes(self, code: str, error: str, analysis: dict) -> dict:
        """Generate three different fixes using Groq API"""
        try:
            prompt = self._create_enhanced_prompt(code, error, analysis)
            response = self._call_groq_api(prompt)
            return self.formatter.parse_ai_response(response)

        except Exception as e:
            error_msg = f"❌ API Error: {str(e)}"
            return {
                "explanation": error_msg,
                "solution1": "Please check your API key and internet connection",
                "solution2": "Ensure the Groq API key is valid and has credits",
                "solution3": "Try again later or use a different model",
            }

    def _create_enhanced_prompt(self, code: str, error: str, analysis: dict) -> str:
        """Create enhanced prompt with STRICT formatting requirements"""

        prompt_parts = []
        prompt_parts.append(
            "IMPORTANT: You MUST provide EXACTLY THREE different solutions in the specified format below. Each solution must be genuinely different."
        )
        prompt_parts.append("")
        prompt_parts.append("CODE TO ANALYZE:")
        prompt_parts.append(f"```python")
        prompt_parts.append(code)
        prompt_parts.append(f"```")
        prompt_parts.append("")
        prompt_parts.append("ERROR MESSAGE:")
        prompt_parts.append(error)
        prompt_parts.append("")
        prompt_parts.append(
            "YOUR RESPONSE MUST FOLLOW THIS EXACT FORMAT - NO DEVIATIONS:"
        )
        prompt_parts.append("")
        prompt_parts.append("ERROR EXPLANATION:")
        prompt_parts.append(
            "[Provide a clear, one-paragraph explanation of what caused the error and why it happened]"
        )
        prompt_parts.append("")
        prompt_parts.append("SOLUTION 1 (SIMPLE FIX):")
        prompt_parts.append(
            "[Provide the SIMPLEST possible fix that a beginner would understand. This should be a direct code correction with minimal changes.]"
        )
        prompt_parts.append("")
        prompt_parts.append("SOLUTION 2 (TRY-EXCEPT HANDLING):")
        prompt_parts.append(
            "[Provide a ROBUST error handling solution using try-except blocks. Include specific exception types and proper error messages. This should be production-quality code.]"
        )
        prompt_parts.append("")
        prompt_parts.append("SOLUTION 3 (ALTERNATIVE APPROACH):")
        prompt_parts.append(
            "[Provide a COMPLETELY DIFFERENT approach to solve the same problem. This could involve refactoring, using different libraries, or implementing best practices. This should not be just another variation of the first two solutions.]"
        )
        prompt_parts.append("")
        prompt_parts.append("CRITICAL REQUIREMENTS:")
        prompt_parts.append("1. All three solutions MUST be different from each other")
        prompt_parts.append("2. Solution 1 must be the simplest direct fix")
        prompt_parts.append(
            "3. Solution 2 must include proper try-except error handling"
        )
        prompt_parts.append("4. Solution 3 must be a fundamentally different approach")
        prompt_parts.append("5. Each solution must include actual Python code examples")
        prompt_parts.append("6. Do NOT skip any of the three solutions")
        prompt_parts.append("")
        prompt_parts.append("Now provide your analysis:")

        return "\n".join(prompt_parts)

    def _call_groq_api(self, prompt: str) -> str:
        """Make API call to Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Python developer. You MUST provide exactly three different solutions for every bug: 1) Simple fix, 2) Try-except handling, 3) Alternative approach. Always follow the exact format specified.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,  # Increased for more diverse solutions
                max_tokens=3000,  # Increased for longer responses
                top_p=0.9,
            )
            return response.choices[0].message.content
        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Debug: Groq API call failed: {e}")
            raise e

    def test_fix_in_sandbox(self, fixed_code: str) -> dict:
        """Optionally test AI-suggested fix in a sandboxed subprocess"""
        result = {"success": False, "output": "", "error": ""}

        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".py", mode="w"
            ) as tmp_file:
                tmp_file.write(fixed_code)
                tmp_path = tmp_file.name

            process = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )

            result["output"] = process.stdout.strip()
            result["error"] = process.stderr.strip()
            result["success"] = process.returncode == 0

        except subprocess.TimeoutExpired:
            result["error"] = "Execution timed out (possible infinite loop)"
        except Exception as e:
            result["error"] = f"Sandbox error: {e}"

        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        return result
