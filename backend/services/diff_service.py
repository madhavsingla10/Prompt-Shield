import difflib
from typing import List, Optional

class DiffService:
    """
    Utility service for generating unified text diffs and inspecting prompt transformations.
    """

    @staticmethod
    def generate_unified_diff(original: str, modified: str, from_name: str = "Original Prompt", to_name: str = "Hardened Prompt") -> str:
        """Generates unified diff between original and hardened prompts."""
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=from_name,
            tofile=to_name,
            lineterm=""
        )
        return "".join(diff)

    @staticmethod
    def extract_xml_tags(prompt: str) -> List[str]:
        """Extracts XML tag demarcation markers present in a hardened prompt."""
        import re
        tags = re.findall(r"<([a-zA-Z0-9_\-]+)>", prompt)
        return [f"<{t}>" for t in set(tags)]

diff_service = DiffService()
