import logging
import sys
import time
from typing import Optional

# Setup standard logging if not already configured
def init_agent_logging():
    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

init_agent_logging()

class BaseAgent:
    """
    Abstract superclass for all PromptShield Arena Agents.
    Adheres to the llm_engineering logging, coloring, and lifecycle design patterns.
    """

    # Foreground colors (ANSI)
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background color
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    
    # Reset code
    RESET = '\033[0m'

    # Agent specific color mapping
    COLOR_PALETTE = {
        "AttackerAgent": RED,
        "SandboxAgent": YELLOW,
        "EvaluatorAgent": MAGENTA,
        "CompilerAgent": CYAN,
        "VerifierAgent": GREEN,
        "VectorStoreAgent": BLUE,
        "AgentFramework": WHITE
    }

    name: str = "BaseAgent"

    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        self.color = self.COLOR_PALETTE.get(self.name, self.WHITE)
        self.logger = logging.getLogger(self.name)

    def log(self, message: str) -> None:
        """Log this as an info message, visually identifying the agent in terminal."""
        color_code = self.BG_BLACK + self.color
        formatted_message = f"{color_code}[{self.name}] {message}{self.RESET}"
        self.logger.info(formatted_message)

    def log_section(self, section_name: str) -> None:
        """Visual demarcation banner for major agent milestones."""
        banner = f"\n{'=' * 15} [{self.name}] {section_name} {'=' * 15}"
        self.log(banner)
