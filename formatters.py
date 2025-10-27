import re
from config import Config


class OutputFormatter:
    @staticmethod
    def parse_ai_response(response: str) -> dict:
        """Parse AI response into structured format with robust error handling"""
        sections = {
            "explanation": "No explanation provided",
            "solution1": "No simple fix provided",
            "solution2": "No try-except solution provided",
            "solution3": "No alternative approach provided",
        }

        # Clean the response
        response = response.strip()

        # Multiple parsing strategies
        parsed = OutputFormatter._parse_with_regex(response)
        if parsed:
            return parsed

        # Fallback parsing
        parsed = OutputFormatter._parse_fallback(response)
        if parsed:
            return parsed

        # Ultimate fallback - return the raw response
        sections["explanation"] = response
        return sections

    @staticmethod
    def _parse_with_regex(response: str) -> dict:
        """Parse using regex patterns"""
        sections = {
            "explanation": "",
            "solution1": "",
            "solution2": "",
            "solution3": "",
        }

        try:
            # More flexible regex patterns - Pattern 1: Standard format
            patterns = [
                r"ERROR EXPLANATION:\s*(.*?)(?=SOLUTION 1|SOLUTION 2|SOLUTION 3|$)",
                r"SOLUTION 1 \(SIMPLE FIX\):\s*(.*?)(?=SOLUTION 2|SOLUTION 3|$)",
                r"SOLUTION 2 \(TRY-EXCEPT HANDLING\):\s*(.*?)(?=SOLUTION 3|$)",
                r"SOLUTION 3 \(ALTERNATIVE APPROACH\):\s*(.*?)$",
            ]

            explanation_match = re.search(
                patterns[0], response, re.DOTALL | re.IGNORECASE
            )
            solution1_match = re.search(
                patterns[1], response, re.DOTALL | re.IGNORECASE
            )
            solution2_match = re.search(
                patterns[2], response, re.DOTALL | re.IGNORECASE
            )
            solution3_match = re.search(
                patterns[3], response, re.DOTALL | re.IGNORECASE
            )

            if explanation_match:
                sections["explanation"] = explanation_match.group(1).strip()
            if solution1_match:
                sections["solution1"] = solution1_match.group(1).strip()
            if solution2_match:
                sections["solution2"] = solution2_match.group(1).strip()
            if solution3_match:
                sections["solution3"] = solution3_match.group(1).strip()

            # If we found at least 3 sections, return
            if sum(1 for v in sections.values() if v.strip()) >= 3:
                return sections

            # Pattern 2: Alternative format
            patterns2 = [
                r"ERROR EXPLANATION:\s*(.*?)(?=SOLUTION 1|$)",
                r"SOLUTION 1:\s*(.*?)(?=SOLUTION 2|$)",
                r"SOLUTION 2:\s*(.*?)(?=SOLUTION 3|$)",
                r"SOLUTION 3:\s*(.*?)$",
            ]

            explanation_match2 = re.search(
                patterns2[0], response, re.DOTALL | re.IGNORECASE
            )
            solution1_match2 = re.search(
                patterns2[1], response, re.DOTALL | re.IGNORECASE
            )
            solution2_match2 = re.search(
                patterns2[2], response, re.DOTALL | re.IGNORECASE
            )
            solution3_match2 = re.search(
                patterns2[3], response, re.DOTALL | re.IGNORECASE
            )

            if explanation_match2 and not sections["explanation"]:
                sections["explanation"] = explanation_match2.group(1).strip()
            if solution1_match2 and not sections["solution1"]:
                sections["solution1"] = solution1_match2.group(1).strip()
            if solution2_match2 and not sections["solution2"]:
                sections["solution2"] = solution2_match2.group(1).strip()
            if solution3_match2 and not sections["solution3"]:
                sections["solution3"] = solution3_match2.group(1).strip()

        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Debug: Regex parsing failed: {e}")

        # Only return if we have substantial content
        if sum(1 for v in sections.values() if v.strip()) >= 2:
            return sections

        return None

    @staticmethod
    def _parse_fallback(response: str) -> dict:
        """Fallback parsing using line-based approach"""
        sections = {
            "explanation": "",
            "solution1": "",
            "solution2": "",
            "solution3": "",
        }

        lines = response.split("\n")
        current_section = "explanation"
        current_content = []

        for line in lines:
            line = line.strip()

            # Detect section headers
            if "ERROR EXPLANATION" in line.upper():
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "explanation"
                current_content = []
            elif "SOLUTION 1" in line.upper() or "SIMPLE FIX" in line.upper():
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "solution1"
                current_content = []
            elif "SOLUTION 2" in line.upper() or "TRY-EXCEPT" in line.upper():
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "solution2"
                current_content = []
            elif "SOLUTION 3" in line.upper() or "ALTERNATIVE" in line.upper():
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "solution3"
                current_content = []
            else:
                current_content.append(line)

        # Don't forget the last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        # Only return if we have substantial content
        if sum(1 for v in sections.values() if len(v) > 10) >= 2:
            return sections

        return None

    @staticmethod
    def format_final_output(result: dict) -> str:
        """Format the final output for display"""
        # Ensure we have content for all sections
        output = f"""
🐛 **ERROR EXPLANATION:**
{result['explanation'] if result['explanation'].strip() else 'No explanation provided'}

🔧 **SOLUTION 1 (SIMPLE FIX):**
{result['solution1'] if result['solution1'].strip() else 'No simple fix provided'}

🛡️ **SOLUTION 2 (TRY-EXCEPT HANDLING):**
{result['solution2'] if result['solution2'].strip() else 'No try-except solution provided'}

💡 **SOLUTION 3 (ALTERNATIVE APPROACH):**
{result['solution3'] if result['solution3'].strip() else 'No alternative approach provided'}
"""
        return output
