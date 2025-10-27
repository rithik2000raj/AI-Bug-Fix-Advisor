import re
from config import Config


class ChunkProcessor:
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.overlap_size = Config.OVERLAP_SIZE
        self.context_lines = Config.CONTEXT_LINES

    def chunk_code(self, code: str) -> list:
        """Split code into chunks with overlapping context for better error understanding"""
        if not code or len(code.strip()) == 0:
            return []

        lines = code.split("\n")

        # If code is small enough, return as single chunk
        if len(lines) <= self.chunk_size:
            return [code]

        chunks = []
        i = 0

        while i < len(lines):
            # Calculate chunk end
            chunk_end = min(i + self.chunk_size, len(lines))

            # Extract chunk
            chunk_lines = lines[i:chunk_end]

            # Add overlapping context from previous chunk if not first chunk
            if i > 0 and self.overlap_size > 0:
                overlap_start = max(0, i - self.overlap_size)
                overlap_lines = lines[overlap_start:i]
                chunk_lines = overlap_lines + chunk_lines

            chunks.append("\n".join(chunk_lines))

            # Move to next chunk position
            i += self.chunk_size - self.overlap_size

        return chunks

    def get_error_context(self, code: str, error_line: int) -> str:
        """Extract context around the error line for better analysis"""
        lines = code.split("\n")

        # Adjust for 0-based indexing
        error_line_idx = max(0, error_line - 1)

        start_line = max(0, error_line_idx - self.context_lines)
        end_line = min(len(lines), error_line_idx + self.context_lines + 1)

        context_lines = lines[start_line:end_line]

        # Add line numbers for clarity
        numbered_context = []
        for i, line in enumerate(context_lines, start=start_line + 1):
            marker = ">>> " if i == error_line else "    "
            numbered_context.append(f"{marker}Line {i}: {line}")

        return "\n".join(numbered_context)

    def extract_error_details(self, error_traceback: str) -> dict:
        """Extract key error details from traceback"""
        error_details = {
            "error_type": "UnknownError",
            "error_message": "Unknown error",
            "line_number": None,
            "file_name": None,
        }

        try:
            # Pattern to match Python traceback error lines
            patterns = [
                r'File "([^"]+)", line (\d+).*\n.*(\w+): (.+)',
                r"(\w+Error): (.+)",
                r"(\w+): (.+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, error_traceback)
                if match:
                    if len(match.groups()) == 4:
                        error_details["file_name"] = match.group(1)
                        error_details["line_number"] = int(match.group(2))
                        error_details["error_type"] = match.group(3)
                        error_details["error_message"] = match.group(4)
                    elif len(match.groups()) == 2:
                        error_details["error_type"] = match.group(1)
                        error_details["error_message"] = match.group(2)
                    break

            return error_details
        except Exception as e:
            if Config.DEBUG_MODE:
                print(f"Debug: Error parsing failed: {e}")
            return error_details
