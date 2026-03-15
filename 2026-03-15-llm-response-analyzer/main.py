"""
Project Name: LLM Response Quality Analyzer
Goal Area: AI & Automation Mastery
Description: A tool to evaluate LLM responses against customizable quality metrics like readability, word count, and keyword density.
Author: Sivanesh (via Gemini CLI Agent)
Date: 2026-03-15
"""

import re
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Optional: pip install textstat rich
try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

@dataclass
class QualityReport:
    """Data class to hold analysis results."""
    word_count: int
    char_count: int
    readability_score: float
    reading_ease: str
    keyword_matches: Dict[str, bool]
    sentiment_estimate: str
    is_valid_json: bool

class ResponseAnalyzer:
    """Analyzes text responses based on AI quality standards."""
    
    def __init__(self, target_keywords: List[str] = None):
        self.target_keywords = target_keywords or []
        self.console = Console() if HAS_RICH else None

    def _get_readability(self, text: str) -> tuple:
        """Calculates Flesch Reading Ease score."""
        if HAS_TEXTSTAT:
            score = textstat.flesch_reading_ease(text)
            if score >= 90: ease = "Very Easy"
            elif score >= 80: ease = "Easy"
            elif score >= 70: ease = "Fairly Easy"
            elif score >= 60: ease = "Standard"
            elif score >= 50: ease = "Fairly Difficult"
            elif score >= 30: ease = "Difficult"
            else: ease = "Very Confusing"
            return score, ease
        return 0.0, "N/A (textstat missing)"

    def _check_json(self, text: str) -> bool:
        """Checks if text contains valid JSON."""
        try:
            # Try to find JSON block in markdown
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                json.loads(json_match.group(1))
            else:
                json.loads(text)
            return True
        except (json.JSONDecodeError, AttributeError):
            return False

    def analyze(self, text: str) -> QualityReport:
        """Performs full analysis of the provided text."""
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        score, ease = self._get_readability(text)
        
        keyword_matches = {kw: bool(re.search(rf'\b{kw}\b', text, re.IGNORECASE)) 
                          for kw in self.target_keywords}
        
        # Simple heuristic for sentiment
        pos_words = {'excellent', 'good', 'success', 'helpful', 'correct', 'efficient'}
        neg_words = {'bad', 'error', 'fail', 'wrong', 'slow', 'poor'}
        
        pos_count = sum(1 for w in words if w.lower() in pos_words)
        neg_count = sum(1 for w in words if w.lower() in neg_words)
        
        if pos_count > neg_count: sentiment = "Positive"
        elif neg_count > pos_count: sentiment = "Negative"
        else: sentiment = "Neutral"

        return QualityReport(
            word_count=word_count,
            char_count=char_count,
            readability_score=score,
            reading_ease=ease,
            keyword_matches=keyword_matches,
            sentiment_estimate=sentiment,
            is_valid_json=self._check_json(text)
        )

    def display_report(self, text: str, report: QualityReport):
        """Prints a formatted report to the console."""
        if HAS_RICH:
            self.console.print(Panel("[bold blue]LLM Response Quality Analysis[/bold blue]"))
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="dim")
            table.add_column("Value")
            
            table.add_row("Word Count", str(report.word_count))
            table.add_row("Readability Score", f"{report.readability_score:.2f}")
            table.add_row("Reading Ease", report.reading_ease)
            table.add_row("Sentiment", report.sentiment_estimate)
            table.add_row("JSON Valid", "✅" if report.is_valid_json else "❌")
            
            self.console.print(table)
            
            if report.keyword_matches:
                self.console.print("\n[bold]Keyword Checklist:[/bold]")
                for kw, found in report.keyword_matches.items():
                    status = "[green]Found[/green]" if found else "[red]Missing[/red]"
                    self.console.print(f" • {kw}: {status}")
        else:
            print("-" * 30)
            print("QUALITY REPORT")
            print(f"Words: {report.word_count}")
            print(f"Readability: {report.reading_ease} ({report.readability_score})")
            print(f"Sentiment: {report.sentiment_estimate}")
            print(f"JSON: {report.is_valid_json}")
            print("-" * 30)

if __name__ == "__main__":
    # Sample LLM response for testing
    sample_text = """
    I have analyzed your request for a portfolio rebalancer. 
    The solution is efficient and follows all financial best practices. 
    Here is the configuration in JSON format:
    ```json
    {"target_allocation": {"stocks": 0.7, "bonds": 0.3}}
    ```
    This should help you achieve your goals effectively.
    """
    
    analyzer = ResponseAnalyzer(target_keywords=["portfolio", "JSON", "stocks", "risk"])
    report = analyzer.analyze(sample_text)
    analyzer.display_report(sample_text, report)
