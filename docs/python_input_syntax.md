# Python input syntax error troubleshooting

If you're seeing a syntax error with this code:

```python
name = input("enter name: ")
age = int(input("enter age: "))
marks = float(input("enter marks: "))

print("welcome", name)
print("age =", age)
print("marks =", marks)
```

## Common cause

The snippet in your message ends with extra characters:

```
..... im getting synatc error for this while exectuing
```

Those dots and trailing text are not valid Python syntax. Make sure you **only** run the
Python code above and **remove** any trailing text or punctuation after it.

## Example of a valid file

Save only the Python code in a file like `main.py` and run it:

```bash
python main.py
```

