# Flopz - Firmware Liberation on Python
[![Python application](https://github.com/Flopz-Project/flopz/actions/workflows/python-app.yml/badge.svg)](https://github.com/Flopz-Project/flopz/actions/workflows/python-app.yml)

Flopz is an assembler toolkit written in pure python. Use it to:
- Create shellcode for embedded systems
- Dynamically patch large collections of binaries
- Instrument firmware images, for debugging and fuzzing

### Currently, Flopz supports:
- ARM: Thumb Mode
- PPC: VLE, only
- RISC-V: RV32I, RV32C
- IA-32

If you'd like to see another architecture implemented, feel free to reach out anytime - we enjoy doing this!

### What makes Flopz different from keystone, rasm2, gcc* etc. ?
Instead of just turning assembly strings into bytes, Flopz aims to make interactive patching and instrumenting firmware easier.
For this, it provides a low-level instruction and register API that allows you to build up shellcode, modules and functions directly in python, without dealing with strings of assembly syntax.

In embedded security testing, no device is like another: Because of this, we provide an object-oriented approach for defining custom targets, so that as many components as possible can be reused across projects involving different devices & processor architectures.

Since Flopz has been written from scratch in pure python, it may not support as many architectures as other tools (such as those based on Clang/LLVM).
However, it is our goal to cover exactly those architectures that matter to embedded security people which may not be covered by other tools.
Also, extending Flopz is made less challenging through a maintained set of unit tests and code documentation.

Flopz is meant to work together with other tools. In particular, there is a [Ghidra Extension](https://github.com/Flopz-Project/flopz-ghidra) which helps you instrument firmware directly in Ghidra.

### Documentation
The provided [documentation](https://flopz-project.github.io/flopz) makes it easy to work with flopz and use its interface in your projects.
