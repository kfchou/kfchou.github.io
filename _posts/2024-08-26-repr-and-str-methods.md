---
layout: post
title:  __repr__ and __str__ methods in python classes
categories: [Python,Tutorials]
---

Understanding these closely related methods can help us write better classes. The devs who use your code will thank you!

General concepts:

`__repr__`: Should return a string that is a valid Python expression that could be used to recreate the object (ideally). It's mainly used for debugging and development. The goal is to provide an “official” string representation of the object.

`__str__`: Should return a human-readable string representation of the object. This is what gets printed by default when you print an object.

## From the user perspective
When calling a variable interactively, its `__repr__` method is called. 

```py
>>> a = 'hello'
>>> a
'hello'
```
When calling the variable inside of a `print()` statement, its `__str__` method is called:
```
>>> print(a)
hello
```

## From the developer perspective
Let's write a class with custom repr and str methods:
```py
class MyClass:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"MyClass(value={self.value!r})"

    def __str__(self):
        return f"MyClass with value: {self.value}"
```

From the user perspective, it will look like:
```py
>>> obj = MyClass(42)
>>> repr(obj) # the __repr__ method returns a string
'MyClass(value=42)'
>>> print(obj) # the print() function calls the __str__ method of "obj".
MyClass with value: 42
>>> obj # when called interactively, we're implicitly calling print(repr(obj))
MyClass(value=42)
```
You can call the `__str__` representation of an object by calling `str(obj)`, which implicitly calls the object's `__str__` method:

```py
>>> str(obj) # this calls the __repr__ of the string object, so you get the single quotes. See the a = 'hello' example above.
'MyClass with value: 42'
>>> print(str(obj)) # and this calls the __str__ of the string object
MyClass with value: 42
```

## f-string specifiers
We can specify f-strings to show the `__repr__` or `__str__ ` of an object.
```py
>>> print(f'{a!r}') # the __repr__ method is called
'hello'
>>> print(f'{a!s}') # the __str__ method is called
hello
```

## Example code for you to play around with:
```py
class MyClass:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"MyClass(value={self.value!r})"

    def __str__(self):
        return f"MyClass with value: {self.value}"

def main():
    # Example usage
    obj = MyClass(42)
    print(repr(obj))  # Output: MyClass(value=42)
    print(str(obj))   # Output: MyClass with value: 42

if __name__=='__main__':
    main()
```