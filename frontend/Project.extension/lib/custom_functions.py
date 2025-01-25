class ContextData:
    def __init__(self):
        self._context = ""  # Notice the underscore, it denotes a private attribute
        self._counter = 1

    @property
    def context(self):
        """The context property."""
        return self._context

    @context.setter
    def context(self, value):
        if isinstance(value, str):
            self._context = value  # Set the private attribute, not the property itself
        else:
            raise ValueError("Context must be a string")

    @context.deleter
    def context(self):
        self._context = None

    @property
    def counter(self):
        """The counter property."""
        return self._counter

    @counter.setter
    def counter(self, value):
        if isinstance(value, int) and value >= 0:
            self._counter = value  # Set the private attribute, not the property itself
        else:
            raise ValueError("Counter must be a non-negative integer")

    def increment_counter(self):
        """Increment the counter property by 1."""
        self._counter += 1

def clean_response_string(response):
    # Convert bytes to string if needed
    if isinstance(response, bytes):
        response = response.decode('utf-8')
    
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- "
    cleaned_string = ''.join(c for c in response if c in allowed_chars)
    return cleaned_string

def clean_code_snippet(snippet):
    # Convert bytes to string if needed
    if isinstance(snippet, bytes):
        snippet = snippet.decode('utf-8')
    
    # Split the snippet into lines
    lines = []
    current_indent = 0
    
    # Process each line
    for line in snippet.split('\n'):
        # Skip empty lines and comment-only lines
        line = line.rstrip()
        if not line or line.strip().startswith(('```', '#', 'This script')):
            continue
            
        # Handle indentation
        stripped_line = line.lstrip()
        if stripped_line:
            # If line starts with certain keywords, reduce indent
            if any(stripped_line.startswith(word) for word in ['else:', 'except:', 'finally:']):
                current_indent = max(0, current_indent - 1)
            
            # Add the line with proper indentation
            lines.append('    ' * current_indent + stripped_line)
            
            # If line ends with colon, increase indent for next line
            if stripped_line.endswith(':'):
                current_indent += 1
    
    # Join the lines back together
    clean_snippet = '\n'.join(lines)
    
    # Replace problematic code patterns
    replacements = {
        'duct.Diameter': 'get_duct_size(duct)',
        'largest_duct = max(ducts, key=lambda duct: duct.Diameter)': 'largest_duct = max(ducts, key=get_duct_size)',
    }
    
    for old, new in replacements.items():
        clean_snippet = clean_snippet.replace(old, new)
    
    # Add helper function for duct size
    helper_function = '''
def get_duct_size(duct):
    try:
        # Try to get diameter for round ducts
        return duct.Diameter
    except:
        try:
            # For rectangular ducts, use the larger dimension
            height = duct.get_Parameter(BuiltInParameter.RBS_CURVE_HEIGHT_PARAM).AsDouble()
            width = duct.get_Parameter(BuiltInParameter.RBS_CURVE_WIDTH_PARAM).AsDouble()
            return max(height, width)
        except:
            # If both fail, return 0
            return 0
'''
    
    # Add imports if needed
    if 'BuiltInParameter' not in clean_snippet and 'get_duct_size' in clean_snippet:
        clean_snippet = 'from Autodesk.Revit.DB import BuiltInParameter\n' + clean_snippet
    
    # Add helper function if needed
    if 'get_duct_size' in clean_snippet and helper_function not in clean_snippet:
        clean_snippet = helper_function + '\n' + clean_snippet
    
    return clean_snippet
