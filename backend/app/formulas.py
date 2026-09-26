"""
Formula extraction and processing module.
"""

import re
from typing import List, Dict, Optional, Tuple
from sympy import sympify, SympifyError
from sympy.parsing.latex import parse_latex
import sympy as sp


class FormulaExtractor:
    """Extracts and processes mathematical formulas from text."""
    
    def __init__(self):
        # Patterns for detecting formulas
        self.formula_patterns = [
            # LaTeX formulas
            r'\$\$(.*?)\$\$',  # Display mode: $$...$$
            r'\$(.*?)\$',       # Inline mode: $...$
            r'\\begin\{(equation|eqnarray|align|gather)\}(.*?)\\end\{\1\}',
            
            # Common mathematical expressions
            r'[a-zA-Z]+\s*[=<>]\s*.+',  # x = y
            r'[a-zA-Z]+\s*[+\-*/^]\s*[a-zA-Z0-9]+',  # x + y
            r'[a-zA-Z]+\s*[=<>]\s*[a-zA-Z0-9]+\s*[+\-*/^]\s*.+',
            r'\\frac\{.*?\}\{.*?\}',  # \frac{}{}
            r'\\sqrt\{.*?\}',          # \sqrt{}
            r'\\int\s*.*?\s*d[a-zA-Z]+',  # \int ... dx
            r'\\sum\s*.*?',             # \sum
            r'\\prod\s*.*?',            # \prod
            r'[a-zA-Z]+\s*[=<>]\s*[a-zA-Z0-9]+\s*[+\-*/^]\s*[a-zA-Z0-9]+',
            
            # Chemical formulas
            r'[A-Z][a-z]?[0-9]*',  # Chemical elements
            
            # Physical formulas
            r'[Ff]\s*[=]\s*.*[mM]\s*[aA]',  # F = ma
            r'[Ee]\s*[=]\s*.*[mM][cC]\^2',  # E = mc^2
        ]
        
        # Symbols and operators
        self.math_symbols = {
            '+', '-', '*', '/', '^', '=', '<', '>', '≤', '≥', '≈', '≠',
            '∑', '∏', '∫', '√', '∆', '∇', '∈', '∉', '∀', '∃', '∴', '∵',
            'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ',
            'ν', 'ξ', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ψ', 'ω',
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp',
        }
        
        # Common formula contexts
        self.context_keywords = {
            'formule', 'formula', 'équation', 'equation', 'théorème', 'theorem',
            'loi', 'law', 'principe', 'principle', 'démonstration', 'proof',
            'calcul', 'calculation', 'résultat', 'result',
        }
    
    def extract_formulas(self, text: str, confidence_threshold: float = 0.7) -> List[Dict]:
        """Extract formulas from text with context."""
        formulas = []
        
        # Extract LaTeX formulas
        latex_formulas = self.extract_latex_formulas(text)
        formulas.extend(latex_formulas)
        
        # Extract inline mathematical expressions
        inline_formulas = self.extract_inline_formulas(text)
        formulas.extend(inline_formulas)
        
        # Extract chemical formulas
        chemical_formulas = self.extract_chemical_formulas(text)
        formulas.extend(chemical_formulas)
        
        # Deduplicate and sort by confidence
        unique_formulas = self.deduplicate_formulas(formulas)
        unique_formulas.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Filter by confidence
        return [f for f in unique_formulas if f.get('confidence', 0) >= confidence_threshold]
    
    def extract_latex_formulas(self, text: str) -> List[Dict]:
        """Extract LaTeX formulas from text."""
        formulas = []
        
        # Display mode: $$...$$
        display_pattern = r'\$\$(.*?)\$\$'
        matches = re.finditer(display_pattern, text, re.DOTALL)
        
        for match in matches:
            latex = match.group(1).strip()
            if latex:
                context = self.get_context(text, match.start(), match.end())
                formulas.append({
                    'content': latex,
                    'latex': f'$${latex}$$',
                    'type': 'latex',
                    'context': context,
                    'confidence': 0.95,
                })
        
        # Inline mode: $...$
        inline_pattern = r'\$(.*?)\$'
        matches = re.finditer(inline_pattern, text, re.DOTALL)
        
        for match in matches:
            latex = match.group(1).strip()
            if latex:
                context = self.get_context(text, match.start(), match.end())
                formulas.append({
                    'content': latex,
                    'latex': f'${latex}$',
                    'type': 'latex',
                    'context': context,
                    'confidence': 0.9,
                })
        
        # Equation environments
        equation_pattern = r'\\begin\{(equation|eqnarray|align|gather)\}(.*?)\\end\{\1\}'
        matches = re.finditer(equation_pattern, text, re.DOTALL)
        
        for match in matches:
            latex = match.group(2).strip()
            if latex:
                context = self.get_context(text, match.start(), match.end())
                formulas.append({
                    'content': latex,
                    'latex': f'\\begin{{{match.group(1)}}}{latex}\\end{{{match.group(1)}}}',
                    'type': 'latex',
                    'context': context,
                    'confidence': 0.95,
                })
        
        return formulas
    
    def extract_inline_formulas(self, text: str) -> List[Dict]:
        """Extract inline mathematical expressions."""
        formulas = []
        
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # Look for mathematical expressions
            expr_matches = re.finditer(
                r'([a-zA-Z]+\s*[=<>]\s*.+?[.!?])|'
                r'([a-zA-Z]+\s*[+\-*/^]\s*[a-zA-Z0-9]+)|'
                r'([a-zA-Z]+\s*[=<>]\s*[a-zA-Z0-9]+\s*[+\-*/^]\s*.+?)',
                sentence
            )
            
            for match in expr_matches:
                expr = match.group(0).strip()
                if self.is_mathematical_expression(expr):
                    context = sentence.strip()
                    formulas.append({
                        'content': expr,
                        'latex': self.to_latex(expr),
                        'type': 'math',
                        'context': context,
                        'confidence': self.calculate_confidence(expr, context),
                    })
        
        return formulas
    
    def extract_chemical_formulas(self, text: str) -> List[Dict]:
        """Extract chemical formulas from text."""
        formulas = []
        
        # Find chemical formulas (e.g., H2O, CO2, C6H12O6)
        chem_pattern = r'\b([A-Z][a-z]?[0-9]*){2,}\b'
        matches = re.finditer(chem_pattern, text)
        
        for match in matches:
            formula = match.group(0)
            if self.is_chemical_formula(formula):
                context = self.get_context(text, match.start(), match.end())
                formulas.append({
                    'content': formula,
                    'latex': formula,
                    'type': 'chemical',
                    'context': context,
                    'confidence': 0.85,
                })
        
        return formulas
    
    def is_mathematical_expression(self, text: str) -> bool:
        """Check if text is a mathematical expression."""
        if not text:
            return False
        
        # Check for mathematical symbols
        has_math_symbol = any(sym in text for sym in ['=', '<', '>', '+', '-', '*', '/', '^'])
        
        # Check for common mathematical patterns
        patterns = [
            r'[a-zA-Z]+\s*[=<>]\s*.+',
            r'[a-zA-Z]+\s*[+\-*/^]\s*[a-zA-Z0-9]+',
            r'\d+\s*[+\-*/^]\s*\d+',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return has_math_symbol
    
    def is_chemical_formula(self, text: str) -> bool:
        """Check if text is a chemical formula."""
        if not text:
            return False
        
        # Chemical formulas typically have:
        # - Capital letters (element symbols)
        # - Lowercase letters (second letter of element symbols)
        # - Numbers (counts)
        # - No spaces
        
        if ' ' in text:
            return False
        
        # Check pattern: capital letter followed by optional lowercase and optional number
        pattern = r'^[A-Z][a-z]?[0-9]*$'
        parts = re.findall(pattern, text)
        
        if len(parts) >= 2:
            return True
        
        return False
    
    def to_latex(self, expression: str) -> str:
        """Convert a simple mathematical expression to LaTeX."""
        # Simple conversion - this could be enhanced
        latex = expression
        
        # Replace common operators
        replacements = {
            '->': '\\rightarrow ',
            '<-': '\\leftarrow ',
            '<=>': '\\leftrightarrow ',
            '=>': '\\Rightarrow ',
            '<=': '\\Leftarrow ',
            '<=>': '\\Leftrightarrow ',
            '^': '^',
            '**': '^',
        }
        
        for old, new in replacements.items():
            latex = latex.replace(old, new)
        
        return f"${latex}$"
    
    def get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around a formula."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        context = text[context_start:context_end].strip()
        
        # Clean up context
        context = re.sub(r'\s+', ' ', context)
        
        return context
    
    def calculate_confidence(self, expression: str, context: str) -> float:
        """Calculate confidence score for a formula."""
        confidence = 0.5
        
        # Check if context contains formula-related keywords
        for keyword in self.context_keywords:
            if keyword.lower() in context.lower():
                confidence += 0.1
        
        # Check expression complexity
        if len(expression) > 20:
            confidence += 0.1
        
        if any(sym in expression for sym in ['=', '<', '>', '∑', '∫', '√']):
            confidence += 0.2
        
        # Cap confidence
        return min(confidence, 0.99)
    
    def deduplicate_formulas(self, formulas: List[Dict]) -> List[Dict]:
        """Remove duplicate formulas."""
        seen = set()
        unique_formulas = []
        
        for formula in formulas:
            content = formula.get('content', '')
            if content not in seen:
                seen.add(content)
                unique_formulas.append(formula)
        
        return unique_formulas
    
    def validate_formula(self, formula: str) -> bool:
        """Validate a mathematical formula."""
        try:
            sympify(formula)
            return True
        except (SympifyError, ValueError):
            return False
    
    def simplify_formula(self, formula: str) -> Optional[str]:
        """Simplify a mathematical formula."""
        try:
            expr = sympify(formula)
            simplified = sp.simplify(expr)
            return str(simplified)
        except (SympifyError, ValueError):
            return None
    
    def solve_equation(self, equation: str, variable: str = 'x') -> Optional[str]:
        """Solve a simple equation."""
        try:
            expr = sympify(equation)
            var = sp.Symbol(variable)
            solutions = sp.solve(expr, var)
            return str(solutions)
        except (SympifyError, ValueError):
            return None
    
    def categorize_formula(self, formula: str, context: str = "") -> str:
        """Categorize a formula by subject."""
        formula_lower = formula.lower()
        context_lower = context.lower()
        
        # Physics
        physics_keywords = ['f=', 'ma', 'force', 'acceleration', 'velocity', 'speed', 
                           'energy', 'work', 'power', 'momentum', 'gravity', 'newton']
        if any(kw in formula_lower or kw in context_lower for kw in physics_keywords):
            return "physics"
        
        # Chemistry
        chemistry_keywords = ['h2o', 'co2', 'na', 'cl', 'chemical', 'mole', 'reaction']
        if any(kw in formula_lower or kw in context_lower for kw in chemistry_keywords):
            return "chemistry"
        
        # Mathematics
        math_keywords = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', 'integral', 'sum', 'limit']
        if any(kw in formula_lower or kw in context_lower for kw in math_keywords):
            return "mathematics"
        
        # Statistics
        stat_keywords = ['mean', 'median', 'mode', 'std', 'variance', 'probability']
        if any(kw in formula_lower or kw in context_lower for kw in stat_keywords):
            return "statistics"
        
        return "unknown"


# Singleton instance
formula_extractor = FormulaExtractor()


# Convenience functions
def extract_formulas(text: str, confidence_threshold: float = 0.7) -> List[Dict]:
    """Extract formulas from text."""
    return formula_extractor.extract_formulas(text, confidence_threshold)


def validate_formula(formula: str) -> bool:
    """Validate a formula."""
    return formula_extractor.validate_formula(formula)


def categorize_formula(formula: str, context: str = "") -> str:
    """Categorize a formula."""
    return formula_extractor.categorize_formula(formula, context)
