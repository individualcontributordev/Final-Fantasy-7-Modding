import os
import subprocess
import re
from unsloth import FastLanguageModel

# 1. Initialize Your Highly Specialized Fine-Tuned Brain
max_seq_length = 4096
model, tokenizer = FastLanguageModel.from_pretrained(
    # model_name = "ff7_coder_lora_model", # Points directly to your saved weights folder
    model_name = "ff7_coder_complete_agent", # Points directly to your saved weights folder
    max_seq_length = max_seq_length,
    load_in_4bit = True,                 # Keeps VRAM under 6GB on your RTX 3070
)
FastLanguageModel.for_inference(model)   # Optimizes the internal kernels for fast token delivery

# 2. Define the Native System Environment Map
WORKSPACE_CONTEXT = """
You are a completely autonomous Agentic Terminal Engine. You operate natively on the user's workstation machine.
You have direct, root-level clearance to view files, write Python automation tools, and execute terminal commands.

📍 HARDCODED WORKSPACE DIRECTORY MAP:
- Personal Reverse Engineering Logs/Notes: ~/Final-Fantasy-7-CSR
- Active Mod Development Workspace:       /mnt/d/projects/Final-Fantasy-7-Modding
- Custom Mod Builder Web Site Repository:  ~/individualcontributordev.github.io
- Reference Engines & Tools:
  * Makou Reactor Source Tree:            ~/makoureactor
  * FF7TK Component Library:             ~/ff7tk
  * Ghidra SRE Installation:              ~/Downloads/ghidra_12.1.2_PUBLIC

🔧 AVAILABLE TOOLS:
To execute actions on the machine, you must wrap your commands in clean executable markdown block tags:
- To run a terminal command, use: ```bash ... ```
- To save or write a python modding script, use: ```python ... ```
"""

# 3. Native Execution Engine (The "Hands")
def execute_system_tool(model_output):
    """Parses the model's text response and executes terminal actions natively."""
    # Find any bash block the model generated
    bash_match = re.search(r"```bash\n(.*?)\n```", model_output, re.DOTALL)
    if bash_match:
        command = bash_match.group(1).strip()
        print(f"\n[AGENT EXECUTING BASH]: {command}")
        
        # Run the command directly on your Ubuntu environment
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return True, output

    # Find any python block the model generated to auto-write files
    python_match = re.search(r"```python\n(.*?)\n```", model_output, re.DOTALL)
    if python_match:
        code = python_match.group(1).strip()
        # Automatically extract target script filename if specified, or default to temp_patch.py
        filename = "temp_patch.py"
        file_target = re.search(r"# TARGET_FILE:\s*(\S+)", code)
        if file_target:
            filename = file_target.group(1)
            
        print(f"\n[AGENT WRITING FILE]: {filename}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        return True, f"Successfully wrote script to file path: {filename}"
        
    return False, "No native tool calls detected."

# 4. Core Conversational Loop
print("🤖 Custom FF7 Autonomous Agent Active and Armed. Enter your command (type 'exit' to quit):")
chat_history = []

while True:
    user_query = input("\n👤 User: ")
    if user_query.lower() == 'exit':
        break
        
    # Build complete execution token frame
    prompt = f"### System:\n{WORKSPACE_CONTEXT}\n\n"
    for role, text in chat_history[-4:]: # Keep a rolling short memory to prevent context blowout
        prompt += f"### {role}:\n{text}\n\n"
    prompt += f"### Instruction:\n{user_query}\n\n### Response:\n"
    
    # Generate token sequence on your RTX 3070
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=1024, use_cache=True)
    response_text = tokenizer.batch_decode(outputs)[0].split("### Response:\n")[-1].replace("</s>", "").strip()
    
    print(f"\n🤖 Agent Response:\n{response_text}")
    
    # Trigger the tool execution loop
    action_taken, tool_result = execute_system_tool(response_text)
    if action_taken:
        print(f"\n💻 System Tool Output:\n{tool_result}")
        # Feed the execution results right back into the model's memory so it knows what happened!
        chat_history.append(("User", user_query))
        chat_history.append(("Response", response_text + f"\n\n[System Notification]: {tool_result}"))
    else:
        chat_history.append(("User", user_query))
        chat_history.append(("Response", response_text))
