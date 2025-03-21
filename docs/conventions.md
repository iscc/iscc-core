# Coding Convetions

## General

**Motto:**

Complexity is not the problem, ambiguity is. Simplicity does not solve ambiguity, clarity does. You
will respond with clarity but will not simplify your response or be ambiguous.

- Write pragmatic, easily testable, and performant code.
- Stick with YAGNI + SOLID + KISS + DRY principles.
- Prefer functional style code with short and pure functions when appropriate.
- Keep the number of function arguments as low as possible.
- Don´t create nested functions.
- Write concise and to-the-point docstrings for all functions.
- When in doubt, choose the most explicit approach that is easiest to reason about.
- When architecting a solution use First Principles Thinking.

## Python Code Style

- Don´t use type annotations in python function signatures.
- Add PEP 484 style type comment as the first line after function definitions.
- Use built-in collection types as generic types for annotations (PEP 585).
- Use the | (pipe) operator for writing union types (PEP 604).
- Write code such that it can be tested without mocking or mokeypatching.
- We use pytest for testing.
- Avoid mocking and monkeypatching in tests at all costs.
- If testing is not possible without mocking/monkeypatching suggest a coderefactor.
- Don´t make python import within function instead make imports at the module level

### Python Example

Example function with PEP 484 style type comment and docstring:

```python
def tokenize_chunks(chunks, max_len=None):
    # type: (list[str], int|None) -> dict
    """
    Tokenize text chunks into model-compatible formats.

    :param chunks: Text chunks to tokenize.
    :param max_len: Truncates chunks above max_len characters
    :return: Dictionary of tokenized data including input IDs, attention masks, and type IDs.
    """
    pass
```

This repository is the normative reference implementation for ISO 24138:2024.
All code edits must be made with the utmost care and attention to detail and with backwards
compatibility in mind. Implementation correctness and performance are crucial.
