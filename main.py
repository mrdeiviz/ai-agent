import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from functions.call_function import call_function
def main():
    
    load_dotenv()
    
    args = sys.argv[1:]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here"')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)


    if args[-1] == "--verbose":        
        user_prompt = " ".join(args[:-1])
    else:
        user_prompt = " ".join(args)

    system_prompt = """
        You are a helpful AI coding agent.

        When a user asks a question or makes a request, make a function call plan. 
        You can perform the following operations:

        - List files and directories
        - Read the content of a file 
        - Write content to a file 
        - Run a Python file with optional arguments

        All paths you provide should be relative to the working directory. 
        You do not need to specify the working directory in your function calls 
        as it is automatically injected for security reasons.
    """

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file
        ]
    )

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    config = types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
    )

    max_iters = 20
    
    for i in range(0,20):

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=config
        )
        
        verbose_flag = False

        if args[-1] == "--verbose":
            verbose_flag = True
            print(f"User prompt: {user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        if response is None or response.usage_metadata is None:
            print("response is malformed")
            return
        
        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None:
                    continue
                messages.append(candidate.content)
        
        if response.function_calls:
            for function_call_part in response.function_calls:
                result = call_function(function_call_part, verbose_flag)
                messages.append(result)
                
        else:
            print(response.text)
            return
    
if __name__ == "__main__":
    main()
