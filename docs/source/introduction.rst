Introduction
============

Welcome to the documentation of the Flopz-Project.

Flopz is an open source assembler toolkit written in pure python. The goal is to make it as easy and convenient as
possible to write shellcode for embedded systems and use this code to patch and instrument firmware for debugging and fuzzing purposes.

Flopz therefore features implementations of several hardware architectures (ARM Thumb, RISC-V, PPC-VLE and more) that allow
for convenient creation and compilation of shellcode snippets in python.

Flopz can be used to instrument target firmware by strategically patching the firmware with shellcode segments we call gadgets.
These gadgets can fulfill task like activating additional periphery, logging important information while the target firmware executes
with minimal overhead or introducing fuzzing input for target functions.

.. note:: We assume that you have the ability to retrieve and flash firmware from and onto your target.

For a rundown of the workflow when using flopz, head over to the :doc:`overview` page.

.. rubric:: Why Flopz?

Instead of just turning assembly strings into bytes, Flopz aims to make interactive patching and instrumenting firmware easier.
For this, it provides a low-level instruction and register API that allows you to build up shellcode, modules and functions directly in python, without dealing with strings of assembly syntax.

In embedded security testing, no device is like another: Because of this, we provide an object-oriented approach for defining custom targets,
so that as many components as possible can be reused across projects involving different devices & processor architectures.

Since Flopz has been written from scratch in pure python, it may not support as many architectures as other tools (such as those based on Clang/LLVM).
However, it is our goal to cover exactly those architectures that matter to embedded security people which may not be covered by other tools.

Check out the :doc:`features page <features>` to find a complete list of flopz feature set.

.. toctree::
   :caption: Contents:
   :maxdepth: 10