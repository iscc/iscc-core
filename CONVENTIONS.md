# Coding Convetions

- Write pragmatic, easily testable, and performant code!
- Prefer short and pure functions where possible!
- Keep the number of function arguments as low as possible!
- Don´t use nested functions!
- Write concise and to-the-point docstrings for all functions!
- Use type comments style (PEP 484) instead of function annotations!
- Always add a correct PEP 484 style type comment as the first line after the function definition!
- Use built-in collection types as generic types for annotations (PEP 585)!
- Use the | (pipe) operator for writing union types (PEP 604)!

Example function with type annotations and docstring:

```python
def tokenize_chunks(chunks, max_len=None):
    # type: (list[str], int|None) -> dict
    """
    Tokenize text chunks into model-compatible formats.

    :param chunks: Text chunks to tokenize.
    :param max_len: Truncates chunks above max_len characters
    :return: Dictionary of tokenized data including input IDs, attention masks, and type IDs.
    """
```
