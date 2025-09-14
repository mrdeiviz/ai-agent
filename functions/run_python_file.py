import os
import subprocess
from google.genai import types

def run_python_file(working_directory: str, file_path: str, args=[]):
    
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_file_path):
        return f'Error: File "{file_path}" not found.'
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        
        final_command = ["python3", file_path]
        final_command.extend(args)
        
        process = subprocess.run(final_command, cwd=abs_working_dir, timeout=30, capture_output=True)
        process_output = f"STDOUT: {process.stdout} - STDERR: {process.stderr}"
        
        if process.stdout == "" and process.stderr == "":
            process_output = "No output produced."
        if process.returncode != 0:
            process_output += f"Process exited with code {process.returncode}"
        
        return process_output
            
            
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file located within the working directory, optionally passing arguments to it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="(Required) The relative or absolute path to the Python file to be executed. Must be inside the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="(Optional) A list of string arguments to pass to the Python file during execution.",
                items=types.Schema(
                    type=types.Type.STRING
                ),
            ),
        },
        required=["file_path"],
    ),
)
