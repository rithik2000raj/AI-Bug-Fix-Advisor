from utils.chunk_processor import ChunkProcessor
from utils.formatters import OutputFormatter
from config import Config
import traceback
import ast


class ErrorParser:
    def __init__(self):
        self.chunk_processor = ChunkProcessor()
        self.formatter = OutputFormatter()

    def analyze_error(self, code: str, error_traceback: str) -> dict:
        """Main method to analyze code and error"""
        if Config.DEBUG_MODE:
            print(
                f"Debug: Analyzing code length: {len(code)}, error: {error_traceback[:100]}..."
            )

        # Extract error details
        error_details = self.chunk_processor.extract_error_details(error_traceback)

        # Get context around error if line number is available
        enhanced_context = ""
        if error_details["line_number"]:
            enhanced_context = self.chunk_processor.get_error_context(
                code, error_details["line_number"]
            )
            if Config.DEBUG_MODE:
                print(
                    f"Debug: Enhanced context extracted around line {error_details['line_number']}"
                )

        analysis_result = {
            "error_details": error_details,
            "needs_chunking": len(code) > Config.CHUNK_SIZE,
            "enhanced_context": enhanced_context,
            "code_length": len(code),
        }

        return analysis_result

    def prepare_for_ai(self, code: str, error_traceback: str, analysis: dict) -> tuple:
        """Prepare data for AI processing"""
        processing_method = "direct"
        content_to_process = code

        if analysis["needs_chunking"] and Config.ENABLE_CHUNKING:
            processing_method = "chunked"
            chunks = self.chunk_processor.chunk_code(code)
            if Config.DEBUG_MODE:
                print(f"Debug: Code split into {len(chunks)} chunks")

        return processing_method, content_to_process

    def analyze_code_structure(self, code: str) -> dict:
        """Optional: Analyze code structure using AST (functions, classes, syntax validity)"""
        analysis = {"functions": [], "classes": [], "syntax_valid": True, "error": None}
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
        except SyntaxError as e:
            analysis["syntax_valid"] = False
            analysis["error"] = f"SyntaxError: {e}"
        return analysis

    def format_traceback(self, exc: Exception) -> str:
        """Optional: Format full traceback into readable string"""
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
