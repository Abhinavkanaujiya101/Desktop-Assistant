import re
import math
import wikipedia
from urllib.request import urlopen
import json

class ReasoningEngine:
    def solve_math_problem(self, problem):
        try:
            # Clean the problem text
            problem_clean = problem.lower().strip()
            
            # Handle algebraic expressions
            if any(word in problem_clean for word in ['x', 'y', 'z', 'algebra', 'equation']):
                return self.solve_algebraic_expression(problem)
            
            # Handle basic arithmetic
            if any(op in problem for op in ['+', '-', '*', '/', '^', '**']):
                # Replace words with operators
                math_expr = problem_clean.replace('plus', '+').replace('add', '+').replace('sum', '+')
                math_expr = math_expr.replace('minus', '-').replace('subtract', '-').replace('difference', '-')
                math_expr = math_expr.replace('multiply by', '*').replace('times', '*').replace('product', '*')
                math_expr = math_expr.replace('divide by', '/').replace('divided by', '/').replace('over', '/')
                math_expr = math_expr.replace('squared', '**2').replace('cubed', '**3')
                math_expr = math_expr.replace('power', '**').replace('^', '**')
                
                # Extract only math-related characters
                math_expr = re.sub(r'[^\d+\-*/().**]', '', math_expr)
                
                if math_expr:
                    # Safe evaluation
                    result = eval(math_expr)
                    return f"The answer is: {result}"
            
            # Handle percentage calculations
            if '%' in problem or 'percent' in problem_clean:
                return self.calculate_percentage(problem)
            
            # Handle square roots
            if 'square root' in problem_clean or 'sqrt' in problem_clean:
                numbers = re.findall(r'\d+', problem)
                if numbers:
                    num = float(numbers[0])
                    result = math.sqrt(num)
                    return f"Square root of {num} = {result:.2f}"
            
            # Handle factorial
            if 'factorial' in problem_clean or '!' in problem:
                numbers = re.findall(r'\d+', problem)
                if numbers:
                    num = int(numbers[0])
                    result = math.factorial(num)
                    return f"Factorial of {num} = {result}"
            
            # If no specific pattern matched, try direct evaluation
            try:
                # Extract numbers and basic operators
                math_expr = re.sub(r'[^\d+\-*/().]', '', problem)
                if any(op in math_expr for op in ['+', '-', '*', '/']):
                    result = eval(math_expr)
                    return f"The answer is: {result}"
            except:
                pass
            
            return "Please provide a clear math problem. Examples: '2+2', '15*3', 'square root of 16'"
                
        except Exception as e:
            return f"Error solving math problem: {str(e)}"
    
    def solve_algebraic_expression(self, problem):
        try:
            problem_lower = problem.lower()
            
            # Simple linear equations: 2x + 3 = 7
            if '=' in problem:
                parts = problem.split('=')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    # Simple case: ax + b = c
                    if 'x' in left and not 'x' in right:
                        # Extract coefficients
                        left = left.replace(' ', '')
                        match = re.match(r'([+-]?\d*)x([+-]\d+)?', left)
                        if match:
                            a = match.group(1)
                            b = match.group(2)
                            
                            a = 1 if a in ['', '+'] else -1 if a == '-' else int(a)
                            b = int(b) if b else 0
                            c = int(right)
                            
                            # Solve: ax + b = c => x = (c - b) / a
                            if a != 0:
                                x = (c - b) / a
                                return f"Solution: x = {x}"
            
            # Handle expressions like "2x + 3x"
            if 'x' in problem_lower and any(op in problem_lower for op in ['+', '-']):
                # Simple combining like terms
                terms = re.findall(r'([+-]?\d*)x', problem_lower)
                if terms:
                    total = 0
                    for term in terms:
                        if term in ['', '+']:
                            total += 1
                        elif term == '-':
                            total -= 1
                        else:
                            total += int(term)
                    return f"Simplified: {total}x"
            
            return "I can solve basic algebraic equations. Try: '2x + 3 = 7' or 'solve 3x = 12'"
            
        except Exception as e:
            return f"Error solving algebraic expression: {str(e)}"
    
    def calculate_percentage(self, problem):
        try:
            numbers = re.findall(r'\d+', problem)
            if len(numbers) >= 2:
                if 'of' in problem.lower():
                    # Percentage of number: 20% of 50
                    percentage = float(numbers[0])
                    number = float(numbers[1])
                    result = (percentage / 100) * number
                    return f"{percentage}% of {number} = {result}"
                else:
                    # What percentage: 25 is what % of 100
                    part = float(numbers[0])
                    whole = float(numbers[1])
                    result = (part / whole) * 100
                    return f"{part} is {result:.1f}% of {whole}"
            return "Please specify percentage calculation clearly. Example: '20% of 50'"
        except Exception as e:
            return f"Error calculating percentage: {str(e)}"
    
    def get_wikipedia_summary(self, topic):
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(topic, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple matches found. Please be more specific."
        except wikipedia.exceptions.PageError:
            return "Sorry, I couldn't find information on that topic."
        except Exception as e:
            return f"Error fetching information: {str(e)}"