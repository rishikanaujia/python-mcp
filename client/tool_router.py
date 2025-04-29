import re
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='tool-router')


class ToolRouter:
    """Tool router for automatically identifying and executing relevant tools."""

    def __init__(self):
        """Initialize the tool router."""
        self.tools = {
            'calculator': {
                'patterns': [
                    # Patterns for different calculator operations
                    {
                        'regex': r'(\d+)\s*\+\s*(\d+)',
                        'operation': 'add',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'(\d+)\s*\-\s*(\d+)',
                        'operation': 'subtract',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'(\d+)\s*\*\s*(\d+)',
                        'operation': 'multiply',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'(\d+)\s*\/\s*(\d+)',
                        'operation': 'divide',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'(\d+)\s*\^\s*(\d+)',
                        'operation': 'power',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    # Support for text expressions like "Calculate 25 times 4"
                    {
                        'regex': r'calculate\s+(\d+)\s+times\s+(\d+)',
                        'operation': 'multiply',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'calculate\s+(\d+)\s+plus\s+(\d+)',
                        'operation': 'add',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'calculate\s+(\d+)\s+minus\s+(\d+)',
                        'operation': 'subtract',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'calculate\s+(\d+)\s+divided\s+by\s+(\d+)',
                        'operation': 'divide',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    # Common "what is" questions
                    {
                        'regex': r'what\s+is\s+(\d+)\s*\+\s*(\d+)',
                        'operation': 'add',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'what\s+is\s+(\d+)\s*\-\s*(\d+)',
                        'operation': 'subtract',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'what\s+is\s+(\d+)\s*\*\s*(\d+)',
                        'operation': 'multiply',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'what\s+is\s+(\d+)\s*\/\s*(\d+)',
                        'operation': 'divide',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'what\s+is\s+(\d+)\s*times\s*(\d+)',
                        'operation': 'multiply',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    },
                    {
                        'regex': r'what\s+is\s+(\d+)\s*divided\s*by\s*(\d+)',
                        'operation': 'divide',
                        'param_extractor': lambda match: {'a': int(match.group(1)), 'b': int(match.group(2))}
                    }
                ]
            },
            'textProcessor': {
                'patterns': [
                    # Patterns for different text processing operations
                    {
                        'regex': r'how many words (?:are )?in (?:the )?(?:sentence|phrase|text)[:\s]*[\"\'](.*?)[\"\']',
                        'operation': 'word_count',
                        'param_extractor': lambda match: {'text': match.group(1)}
                    },
                    {
                        'regex': r'count (?:the )?words in [\"\'](.*?)[\"\']',
                        'operation': 'word_count',
                        'param_extractor': lambda match: {'text': match.group(1)}
                    },
                    {
                        'regex': r'how many characters (?:are )?in [\"\'](.*?)[\"\']',
                        'operation': 'character_count',
                        'param_extractor': lambda match: {'text': match.group(1)}
                    },
                    {
                        'regex': r'convert to uppercase[:\s]*[\"\'](.*?)[\"\']',
                        'operation': 'to_upper_case',
                        'param_extractor': lambda match: {'text': match.group(1)}
                    },
                    {
                        'regex': r'convert to lowercase[:\s]*[\"\'](.*?)[\"\']',
                        'operation': 'to_lower_case',
                        'param_extractor': lambda match: {'text': match.group(1)}
                    }
                ]
            },
            'dataTransformer': {
                'patterns': [
                    # Patterns for data transformation operations
                    {
                        'regex': r'convert json to csv[:\s]*(.*)',
                        'operation': 'json_to_csv',
                        'param_extractor': lambda match: {'json_data': self._parse_json(match.group(1))}
                    },
                    {
                        'regex': r'convert csv to json[:\s]*(.*)',
                        'operation': 'csv_to_json',
                        'param_extractor': lambda match: {'csv_data': match.group(1)}
                    }
                ]
            }
            # Add patterns for other tools as needed
        }

        # Special case handlers for when regex may not be sufficient
        self.special_handlers = {
            'word_count_this_sentence': self._handle_count_words_in_sentence,
            'calculator_in_context': self._handle_calculator_in_context
        }

    def _parse_json(self, json_text):
        """Attempt to parse JSON from text."""
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON-like structure
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, json_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            return []  # Return empty array if parsing fails

    def _handle_count_words_in_sentence(self, prompt):
        """Special handler for counting words in the prompt sentence."""
        if "how many words" in prompt.lower() and "this sentence" in prompt.lower():
            return [{
                'tool': 'textProcessor',
                'operation': 'word_count',
                'params': {'text': prompt}
            }]
        return []

    def _handle_calculator_in_context(self, prompt):
        """Special handler for multi-step calculations embedded in text."""
        results = []

        # Look for multi-step calculation contexts
        if ("calculate" in prompt.lower() or "what is" in prompt.lower()):
            # Check for specific calculation patterns
            multiply_pattern = r'(\d+)\s*\*\s*(\d+)'
            multiply_matches = re.findall(multiply_pattern, prompt)

            for match in multiply_matches:
                results.append({
                    'tool': 'calculator',
                    'operation': 'multiply',
                    'params': {'a': int(match[0]), 'b': int(match[1])}
                })

            # Check for other operations similarly
            add_pattern = r'(\d+)\s*\+\s*(\d+)'
            add_matches = re.findall(add_pattern, prompt)

            for match in add_matches:
                results.append({
                    'tool': 'calculator',
                    'operation': 'add',
                    'params': {'a': int(match[0]), 'b': int(match[1])}
                })

        return results

    # Modify the analyze_prompt method in client/tool_router.py

    def analyze_prompt(self, prompt):
        """Analyze the prompt to identify needed tools."""
        tools_to_use = []
        prompt_lower = prompt.lower()

        # Track tools we've already added to avoid duplicates
        tool_operation_pairs = set()

        # Check special handlers first
        for handler_name, handler_func in self.special_handlers.items():
            handler_results = handler_func(prompt)
            for result in handler_results:
                tool_op_pair = (result['tool'], result['operation'], tuple(sorted(result['params'].items())))
                if tool_op_pair not in tool_operation_pairs:
                    tool_operation_pairs.add(tool_op_pair)
                    tools_to_use.append(result)

        # Then check regex patterns
        for tool_name, tool_info in self.tools.items():
            for pattern in tool_info['patterns']:
                matches = re.finditer(pattern['regex'], prompt_lower, re.IGNORECASE)
                for match in matches:
                    # Extract parameters based on the match
                    try:
                        params = pattern['param_extractor'](match)

                        # Create a tool operation pair for deduplication
                        # Convert params to a hashable format (tuple of sorted items)
                        param_tuple = tuple(sorted(params.items()))
                        tool_op_pair = (tool_name, pattern['operation'], param_tuple)

                        # Only add if we haven't seen this exact tool+operation+params before
                        if tool_op_pair not in tool_operation_pairs:
                            tool_operation_pairs.add(tool_op_pair)
                            tools_to_use.append({
                                'tool': tool_name,
                                'operation': pattern['operation'],
                                'params': params
                            })
                    except Exception as e:
                        logger.error(f"Error extracting parameters for {tool_name}.{pattern['operation']}: {str(e)}")

        # Log detected tools
        if tools_to_use:
            logger.info(f"Detected {len(tools_to_use)} tools for prompt",
                        {'tools': [f"{t['tool']}.{t['operation']}" for t in tools_to_use]})

        return tools_to_use

    def format_results_for_llm(self, tool_results):
        """Format tool results in a way that's useful for the LLM."""
        formatted_results = []

        for result in tool_results:
            tool = result.get('tool', '')
            operation = result.get('operation', '')
            params = result.get('params', {})
            result_data = result.get('result', {})

            # Format the result based on tool type
            if tool == 'calculator':
                params_str = ', '.join([f"{k}={v}" for k, v in params.items()])
                formatted_results.append(
                    f"Calculator {operation}({params_str}) = {result_data}"
                )
            elif tool == 'textProcessor':
                if operation == 'word_count':
                    text = params.get('text', '')
                    formatted_results.append(
                        f"Word count of '{text[:30]}{'...' if len(text) > 30 else ''}' is {result_data}"
                    )
                elif operation == 'character_count':
                    text = params.get('text', '')
                    formatted_results.append(
                        f"Character count of '{text[:30]}{'...' if len(text) > 30 else ''}' is {result_data}"
                    )
                else:
                    formatted_results.append(
                        f"Text processing result ({operation}): {result_data}"
                    )
            else:
                # Generic formatting for other tools
                formatted_results.append(
                    f"Tool result for {tool}.{operation}: {result_data}"
                )

        return "\n".join(formatted_results)