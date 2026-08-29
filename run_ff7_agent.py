import warnings
import logging
import os
import sys
import contextlib
import io

# STEP 1: SILENCE NOISY HUGGINGFACE GENERATION WARNINGS BEFORE LOADING
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("unsloth").setLevel(logging.ERROR)

import subprocess
import re
import time
import datetime
import torch
from unsloth import FastLanguageModel

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
try:
    from rag_retrieve import retrieve as rag_retrieve, format_context as rag_format_context
    RAG_AVAILABLE = True
except Exception as _rag_import_err:
    RAG_AVAILABLE = False
    _rag_import_error_msg = str(_rag_import_err)

print("🚀 Booting your specialized FF7 Agent environment...")
start_boot = time.time()

# 2. Load the exact base student model cores
max_seq_length = 4096
dtype = torch.float16

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = True, # Kept active to protect your 8GB RTX 3070 VRAM footprint
)

# Load and attach your custom fine-tuned ChatML adapters directly on top!
print("🧠 Applying custom fine-tuned Final Fantasy VII adapters...")
model.load_adapter("ff7_coder_lora_model")
FastLanguageModel.for_inference(model)

# TOKENIZER FIX (huggingface/transformers#45488): see train_ff7.py for full
# explanation. transformers v5's LlamaTokenizer.__init__ overwrites
# tokenizer.json's real ByteLevel pre_tokenizer/decoder with a broken
# Metaspace pipeline, causing every space to be dropped during encode and
# Ġ/Ċ raw-BPE-token leakage during decode. Must be patched here too, not
# just in eval_greedy_test.py/train_ff7.py, or every decoded response in
# this interactive loop comes out fused/leaked like "ĊĊToĠfixĠthe...".
from tokenizers import Tokenizer as _RawTokenizer
_raw_tok = _RawTokenizer.from_pretrained("unsloth/DeepSeek-R1-Distill-Llama-8B")
tokenizer.backend_tokenizer.pre_tokenizer = _raw_tok.pre_tokenizer
tokenizer.backend_tokenizer.decoder = _raw_tok.decoder
_probe_ids = tokenizer("You are an expert", add_special_tokens=False).input_ids
assert tokenizer.decode(_probe_ids) == "You are an expert", (
    "Tokenizer pre_tokenizer/decoder patch failed -- fused-word bug still present!"
)
print("✅ Tokenizer pre_tokenizer/decoder patched (ByteLevel restored, Metaspace bug fixed).")

print(f"✔ Specialized FF7 brain loaded natively into VRAM in {time.time() - start_boot:.2f} seconds.")

# 3. System Prompt Persona (Strictly matches train_ff7.py distribution to avoid token drift)
SYSTEM_PROMPT = "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."

# 4. Human-In-The-Loop Execution Engine (Security Controls, Traversal Guard, Backups)
def execute_system_tool(model_output):
    # Robust match to handle cross-platform \r\n or trailing whitespaces inside code blocks
    bash_match = re.search(r"```bash\s*\n(.*?)\n```", model_output, re.DOTALL)
    if bash_match:
        command = bash_match.group(1).strip()
        print(f"\n⚠️  [AGENT REQUESTS BASH EXECUTION]:\n----------------------------------------\n{command}\n----------------------------------------")

        confirm = input("Confirm execution? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("❌ Execution canceled by user.")
            return "ERROR: Bash command execution was rejected by the human operator."

        print(f"\n[RUNNING BASH]: {command}")
        start_tool = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"⏱️ [TOOL TIME]: Bash execution completed in {time.time() - start_tool:.2f} seconds.")
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    python_match = re.search(r"```python\s*\n(.*?)\n```", model_output, re.DOTALL)
    if python_match:
        code = python_match.group(1).strip()
        filename = "temp_patch.py"
        file_target = re.search(r"# TARGET_FILE:\s*(\S+)", code)
        if file_target:
            filename = file_target.group(1)

        # Path Confinement Guard: Flatten traversal attempts to protect local directories
        filename = os.path.basename(filename)

        print(f"\n⚠️  [AGENT REQUESTS FILE WRITE]: {filename}")
        if os.path.exists(filename):
            print(f"🚨 WARNING: '{filename}' already exists in this directory and will be overwritten!")

        confirm = input("Confirm write operation? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("❌ File write operation canceled by user.")
            return "ERROR: File modification script execution was rejected by the human operator."

        # DISASTER RECOVERY SAFEGUARD: Auto-generate a pristine .bak copy before any rewrite
        if os.path.exists(filename) and not os.path.exists(filename + ".bak"):
            import shutil
            try:
                shutil.copy2(filename, filename + ".bak")
                print(f"📦 [SAFEGUARD]: Successfully backed up existing file to {filename}.bak")
            except Exception as backup_error:
                print(f"⚠️ Backup operation failed: {backup_error}. Aborting write for workspace safety.")
                return f"ERROR: System tool could not create file backup safeguard: {backup_error}"

        print(f"\n[AGENT WRITING FILE]: {filename}")
        start_tool = time.time()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"⏱️ [TOOL TIME]: File written in {time.time() - start_tool:.3f} seconds.")
        return f"Successfully wrote script to file path: {filename}"

    return None

FINDINGS_DIR = "docs/findings"
FINDINGS_TEMPLATE = os.path.join(FINDINGS_DIR, "_template.md")


def _slugify(text, max_words=8):
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    slug = "-".join(words[:max_words])
    return slug[:80].rstrip("-") or "untitled"


def _next_findings_path(date_str, slug):
    # Path Confinement Guard: filename is derived purely from a regex-sanitized
    # slug, never from a raw user/model path -- can't escape docs/findings/.
    base = f"{date_str}-{slug}.md"
    path = os.path.join(FINDINGS_DIR, base)
    n = 2
    while os.path.exists(path):
        path = os.path.join(FINDINGS_DIR, f"{date_str}-{slug}-{n}.md")
        n += 1
    return path


def create_finding_doc(model, tokenizer, problem, solution):
    """Draft a docs/findings/YYYY-MM-DD-slug.md entry from the just-verified
    problem/solution turn, following _template.md. Human confirms before any
    write -- same human-in-the-loop gate as execute_system_tool(). This is
    the intended future fine-tuning feed: once enough of these accumulate,
    they can be mined into data/ff7_re_dataset.jsonl (per AGENTS.md rule 3),
    but they are NOT auto-mined here -- that step stays manual and must be
    checked for RETRACTED/SUPERSEDED status before extraction."""
    try:
        with open(FINDINGS_TEMPLATE, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        template = None

    date_str = datetime.date.today().isoformat()
    fallback_template = (
        "# [Title]\n\n## Summary\n\n## Context\n\n## Discovery\n\n"
        "## How we found it\n\n## Why it matters\n\n## Follow-ups\n\n## Sources\n"
    )
    template_text = template if template else fallback_template
    draft_prompt = (
        "A problem was just solved and confirmed working in this workspace. "
        "Draft a findings-journal entry strictly in this template's structure "
        "(fill in every section, keep it factual and concrete -- addresses, "
        "offsets, file paths, commands -- no speculation dressed as fact):\n\n"
        f"{template_text}"
        f"\n\nPROBLEM:\n{problem}\n\nCONFIRMED SOLUTION:\n{solution}\n\n"
        "Also output a single line at the very end: SLUG: <5-8-word-kebab-case-slug>"
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": draft_prompt},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    with contextlib.redirect_stderr(io.StringIO()):
        outputs = model.generate(input_ids=inputs.input_ids, max_new_tokens=1024, use_cache=True)
    raw = tokenizer.decode(outputs[0, inputs.input_ids.shape[-1]:], skip_special_tokens=True).strip()
    raw = re.sub(r"^.*?<\/think>\s*", "", raw, flags=re.DOTALL).strip()

    slug_match = re.search(r"SLUG:\s*([a-z0-9-]+)", raw, re.IGNORECASE)
    slug = _slugify(slug_match.group(1)) if slug_match else _slugify(problem)
    body = re.sub(r"\n?SLUG:\s*[a-z0-9-]+\s*$", "", raw, flags=re.IGNORECASE).strip()
    # Force Date/Status fields to known-good values regardless of what the
    # model drafted, so provenance is always accurate.
    body = re.sub(r"\*\*Date:\*\*.*", f"**Date:** {date_str}  ", body, count=1)
    if "**Status:**" not in body:
        body = body.replace(f"**Date:** {date_str}  ", f"**Date:** {date_str}  \n**Status:** unverified  ", 1)

    path = _next_findings_path(date_str, slug)
    print(f"\n⚠️  [AGENT REQUESTS FINDINGS DOC]: {path}")
    print("----------------------------------------")
    print(body[:1500] + ("\n... [truncated preview]" if len(body) > 1500 else ""))
    print("----------------------------------------")
    confirm = input("Write this findings doc? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("❌ Findings doc write canceled by user.")
        return None

    os.makedirs(FINDINGS_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "\n")
    print(f"📝 [SAVED]: Findings doc written to {path}")
    return path


print("\n🤖 ==================================================================== 🤖")
print("🤖 Custom FF7 Autonomous Agent Active and Armed. (Type 'exit' to quit)   🤖")
print("🤖 ==================================================================== 🤖")

chat_history = []
TRIGGER_COMMANDS = ["!confirm", "!works", "!verify", "!save"]

# 5. Interactive Persistent Shell Loop
while True:
    try:
        user_query = input("\n👤 User: ").strip()
        if not user_query: continue
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down agent loop. Goodbye!")
            break

        # BACKGROUND AUTOMATION ENGINE: Organic growth dataset compiler
        if any(user_query.lower().startswith(cmd) for cmd in TRIGGER_COMMANDS):
            user_turns = [text for role, text in chat_history if role == "user"]
            agent_turns = [text for role, text in chat_history if role == "assistant"]
            if user_turns and agent_turns:
                print("\n⚡ [AUTOMATION]: Harvesting successful workspace parameters...")
                start_auto = time.time()
                last_problem = user_turns[-1]
                last_solution = agent_turns[-1]

                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Format this into a single-line training JSON object:\nPROBLEM: {last_problem}\nSOLUTION: {last_solution}"}
                ]
                ext_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                ext_inputs = tokenizer([ext_prompt], return_tensors="pt").to("cuda")

                with contextlib.redirect_stderr(io.StringIO()):
                    ext_outputs = model.generate(input_ids=ext_inputs.input_ids, max_new_tokens=1024, use_cache=True)

                new_tokens = ext_outputs[0, ext_inputs.input_ids.shape[-1]:]
                raw_json = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                try:
                    clean_json = re.sub(r"^```json\s*|\s*```$", "", raw_json.strip(), flags=re.MULTILINE)
                    os.makedirs("data", exist_ok=True)
                    with open("data/organic_growth.jsonl", "a", encoding="utf-8") as f:
                        f.write(clean_json.strip() + "\n")
                    print("🎉 [SUCCESS]: Dataset expanded organically via command override!")
                except Exception as e:
                    print(f"⚠️ Dataset append skipped: {e}")

                # Also draft a docs/findings/*.md entry from the same verified
                # turn -- these accumulate over time and, once they reach a
                # useful volume, can be manually mined into
                # data/ff7_re_dataset.jsonl for the next fine-tune pass (after
                # the same RETRACTED/SUPERSEDED check used in this session).
                try:
                    create_finding_doc(model, tokenizer, last_problem, last_solution)
                except Exception as e:
                    print(f"⚠️ Findings doc generation skipped: {e}")
            else:
                print("❌ [AUTOMATION]: No conversation history found in this session to harvest yet.")
            continue

        # --- RAG: GROUND THE QUERY IN VENDORED RE SOURCE REPOS (if index exists) ---
        # HARD GROUNDING GATE: eval showed this LoRA fabricates confident,
        # well-formatted answers (fake opcodes, fake tools, fake file paths)
        # when it has no real source to draw from. If retrieval finds nothing
        # above min_score, refuse to generate freely by default -- the user
        # must explicitly opt in to an unverified/ungrounded answer.
        rag_context = ""
        rag_hits = []
        rag_index_missing = False
        if RAG_AVAILABLE:
            try:
                rag_hits = rag_retrieve(user_query, top_k=4)
                rag_context = rag_format_context(rag_hits)
                if rag_hits:
                    print(f"📚 [RAG]: Retrieved {len(rag_hits)} grounding chunk(s) "
                          f"from {', '.join(sorted(set(h['source'] for h in rag_hits)))}")
            except FileNotFoundError:
                rag_index_missing = True  # No index built yet.
            except Exception as rag_err:
                print(f"⚠️ [RAG]: Retrieval skipped due to error: {rag_err}")

        if RAG_AVAILABLE and not rag_index_missing and not rag_hits:
            print("\n🚫 [GROUNDING GATE]: No verified source found in the local RAG "
                  "index for this query (score below threshold). This LoRA has been "
                  "observed to confidently fabricate opcodes/tools/file paths when "
                  "ungrounded -- treat any answer here as unverified speculation.")
            proceed = input("Generate an UNGROUNDED answer anyway? [y/N]: ").strip().lower()
            if proceed != 'y':
                print("❌ Generation skipped -- no verified source for this query.")
                continue

        # --- NATIVE CHATML RUNTIME INFERENCE PASS ---
        # TOPIC-BLEED FIX: observed live -- when a fresh RAG-grounded question
        # follows an unrelated one, this 8B/r=8 LoRA anchors on the *previous*
        # turn's topic from chat_history and answers that instead of the new
        # question, even with correct new RAG context injected (e.g. asked
        # about ImgBurn/EDC verify failures, answered about FIELD.BIN Ghidra
        # base address from the prior turn). Since rag_hits being non-empty
        # means this is a new, independently-answerable grounded question,
        # drop prior chat_history in that case so it can't dominate the
        # current answer. Keep history only for true follow-ups (no fresh RAG
        # hit this turn, e.g. "can you clarify that" on the same topic).
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if not rag_hits:
            for role, text in chat_history[-4:]:
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": text})

        # TRAIN/INFERENCE SHAPE MATCH: train_ff7.py's format_prompts() builds
        # exactly ONE user turn as "{instruction}\n\nReference material
        # retrieved...\n\n{input}". Previously this appended the RAG context
        # as a SEPARATE, PRIOR user message, producing two consecutive
        # "user" turns the LoRA never saw during training -- a second,
        # independent cause of the confabulation symptom (right base fact,
        # invented supporting detail) alongside the tokenizer/sampling bugs.
        # Must stay byte-for-byte identical to train_ff7.py's wrapper text.
        if rag_context:
            user_content = (
                f"{user_query}\n\nReference material retrieved from local "
                f"reverse-engineering source repos (cite file:line when you "
                f"use these):\n\n{rag_context}"
            )
        else:
            user_content = user_query
        messages.append({"role": "user", "content": user_content})

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
        input_length = inputs.input_ids.shape[-1]

        print("🤔 [AGENT]: Processing tokens and thinking on RTX 3070...")
        start_inference = time.time()

        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            outputs = model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=512,
                do_sample=True,  # was missing -- temperature/top_p are no-ops
                                 # under HF's default do_sample=False (greedy),
                                 # which is one candidate cause of identical
                                 # output across different prompts/contexts.
                temperature=0.6,
                top_p=0.95,
                use_cache=True
            )

        elapsed_inference = time.time() - start_inference

        # Decode the output safely by indexing the batch row first
        generated_tokens = outputs[0, input_length:]
        response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        # Cleanly strip leading DeepSeek internal reasoning traces to prevent terminal leakage
        _pre_strip = response_text
        response_text = re.sub(r"^.*?<\/think>\s*", "", response_text, flags=re.DOTALL).strip()

        # DIAGNOSTIC: if stripping the <think> block leaves nothing (model spent
        # its whole budget reasoning, or hit EOS right after </think>), fall back
        # to showing the raw pre-strip text instead of silently printing nothing --
        # an empty "🤖 Agent:" with no error was masking this failure mode.
        if not response_text and _pre_strip:
            print("\n⚠️ [DIAGNOSTIC]: Response was empty after </think> stripping. "
                  "Raw pre-strip generation follows (likely ran out of tokens while "
                  "still reasoning, or emitted EOS immediately after </think>):")
            response_text = _pre_strip.strip()

        print(f"\n🤖 Agent:\n{response_text}")
        print(f"⏱️ [INFERENCE TIME]: Agent response generated in {elapsed_inference:.2f} seconds.")

        chat_history.append(("user", user_query))
        chat_history.append(("assistant", response_text))

        # Check for code block structures to trigger tools securely
        tool_output = execute_system_tool(response_text)
        if tool_output:
            print(f"\n💻 System Tool Output:\n{tool_output}")
            chat_history.append(("system", tool_output))

    except KeyboardInterrupt:
        continue
    except Exception as e:
        print(f"\nRuntime Error: {e}")
        break
