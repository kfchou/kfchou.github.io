---
layout: post
title:  Bug hunting
categories: [debugging]
excerpt: Some handy tools for debugging
---

```py
from pathlib import Path
import functools
import pickle
import hashlib
import json
import pandas as pd
import numpy as np

def hash_function_args(*args, **kwargs):
    def convert_to_bytes(arg):
        if isinstance(arg, np.ndarray):
            return arg.tobytes()
        return pickle.dumps(arg)
    
    args_bytes = [convert_to_bytes(arg) for arg in args]
    kwargs_bytes = {key: convert_to_bytes(value) for key, value in kwargs.items()}
    
    data_bytes = pickle.dumps((args_bytes, kwargs_bytes))
    return hashlib.sha256(data_bytes).hexdigest()
    
def log_inputs_outputs(log_dir: str):
    """A decorator for logging inputs and outputs of a function
    
    Numpy arrays are saved as .npy files and the filename is stored in the log file
    
    Params:
    -------
    log_dir: str
        The directory where the log files will be saved
    
    Example usage:
    ```
    @log_inputs_outputs("logs/my_function")
    def my_function(...):
    ```
    When you call my_function, all inputs and outputs will be saved to the specified directory
    
    To load the results, see:
        validate_logged_call()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            
            # generate hash based on inputs
            call_id = hash_function_args(*args, **kwargs)[:8]
            
            log_entry = {
                "call_id": call_id,
                "args": [],
                "kwargs": {},
                "output": None
            }
            
            def process_value(value, k=None):
                filename = f"{call_id}.npy" if k is None else f"{call_id}_{k}.npy"
                if isinstance(value, pd.Series):
                    np.save(log_path / filename, value.values)
                    return {"__numpy_array__": filename}
                elif isinstance(value, np.ndarray):
                    np.save(log_path / filename, value)
                    return {"__numpy_array__": filename}
                return value
            
            log_entry["args"] = [process_value(arg, idx) for idx, arg in enumerate(args)]
            log_entry["kwargs"] = {k: process_value(v, k) for k, v in kwargs.items()}
            
            result = func(*args, **kwargs)
            log_entry["output"] = process_value(result)
            
            with open(log_path / f"{call_id}.json", 'w') as f:
                json.dump(log_entry, f, indent=2)
                
            return result
        return wrapper
    return decorator
    
def validate_logged_call(log_dir: str, call_id: str, func):
    """Load the logged inputs and outputs, call the function with the logged inputs,
    and compare the returned value with the logged output.
    
    Params:
    -------
    log_dir: str
        The directory where the log files are saved
    call_id: str
        The unique identifier for the logged call
    func: callable
        The function to be called with the logged inputs
    
    Returns:
    --------
    Tuple: result, expected_result
    """
    log_path = Path(log_dir) / f"{call_id}.json"
    
    with open(log_path, 'r') as f:
        log_entry = json.load(f)
    
    def load_value(value):
        if isinstance(value, dict) and "__numpy_array__" in value:
            return np.load(Path(log_dir) / value["__numpy_array__"])
        return value
    
    args = [load_value(arg) for arg in log_entry["args"]]
    kwargs = {k: load_value(v) for k, v in log_entry["kwargs"].items()}
    
    expected_output = load_value(log_entry["output"])
    
    result = func(*args, **kwargs)
    
    return result, expected_output
```