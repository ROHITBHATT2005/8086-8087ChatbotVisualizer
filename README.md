# Assistant 8086 – 8086/8087 Interactive Simulator with Chatbot

**Learn 8086 assembly and 8087 floating-point math the fun way** – a GUI‑driven simulator with a conversational AI assistant. Write assembly code, execute CPU instructions, explore memory, and chat with an intelligent bot that explains everything step by step.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## What is this?

This project simulates the **Intel 8086 microprocessor** and **8087 numeric coprocessor** inside a friendly desktop application. It’s built for students, hobbyists, and anyone curious about how old‑school CPUs work. You can:

- Type assembly instructions and see registers change in real time.
- Ask the chatbot to do math, show memory, or explain concepts.
- Run multi‑line 8086 programs in a built‑in editor.
- Watch flags, stack, and FPU updates live.

No real hardware needed – just click and learn!

---

## Features

### 🔹 8086 CPU Emulation
- 16‑bit registers (AX, BX, CX, DX, SI, DI, BP, SP, segment registers, IP)
- All essential instructions: `MOV`, `ADD`, `SUB`, `MUL`, `DIV`, `INC`, `DEC`, `AND`, `OR`, `XOR`, `NOT`, `SHL`, `SHR`, `PUSH`, `POP`, `CMP`, `JMP`, conditional jumps, `LOOP`, `CALL`, `RET`, `INT`, `ADC`, `SBB`, `NEG`, `CBW`, `CWD`, `TEST`, `LEA`, flag instructions
- Flag support: CF, PF, AF, ZF, SF, OF, DF, IF, TF

### 🔹 8087 FPU Coprocessor
- 8‑level floating‑point stack
- Instructions: `FLD`, `FST`, `FSTP`, `FADD`, `FSUB`, `FMUL`, `FDIV`, `FSQRT`, `FABS`, `FCHS`, `FCOM`, `FINIT`
- Handles real numbers with high precision

### 🔹 1 MB Memory Model
- Byte‑addressable memory with read/write operations
- Dump memory in hex, view stack region
- Fill memory ranges, store/load values

### 🔹 Chatbot Assistant (Natural Language)
- Understands plain English: *"add 5 and 6"*, *"sqrt of 25"*, *"store 1234 at 1000"*
- Answers questions like *"what are flags?"*, *"tell me about 8086 pipelining"*
- Remembers your name and last result (e.g., *"add 3 to last result"*)
- Tells jokes, shows time/date, and runs a step‑by‑step assembly tutorial

### 🔹 GUI Built with Tkinter
- Multi‑line program editor (one instruction per line, supports labels and comments)
- Live CPU / FPU / Memory tabs
- Sidebar with quick action buttons and examples
- Tooltips, modern look, keyboard shortcuts

---
