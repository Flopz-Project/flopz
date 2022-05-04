Overview
========

| This page provides an overview of the workflow when using flopz.
| Check out the :doc:`tutorial <tutorial>` section for more detailed articles on single functions.

.. image:: images/arch_full.png

Ghidra Plugin
_____________

| After aquiring the raw firmware you want to patch with flopz, using the Ghidra Plugin is the preferred and most convenient way to mark the locations of your gadgets.
| `Ghidra <https://ghidra-sre.org/>`_ is an open source reverse engineering tool developed by the NSA and features a plethora of tools to analyze your binary.
| The repository for our Ghidra Plugin can be found `here <https://github.com/Flopz-Project/flopz-ghidra>`_.
| After analyzing and setting up the memory mapping, the plugin makes it convenient to register free sections of flash or RAM for usage by flopz.
 It is also used to mark the instructions and functions you want to instrument. All this information can then be exported into a JSON configuration file that flopz will need to patch your binary.

A more detailed look at the Ghidra Plugin can be found in this :doc:`tutorial <ghidra>`.


Targets and Gadgets
___________________

Snippets of shellcode you write with flopz that serve a distinct purpose are called **gadgets** by us. Because gadgets are regular python objects this allows for highly reusable code.
When wanting to patch a binary with flopz, you usually define a **target** class that includes several methods that return gadgets for different purposes.
Some example gadgets could be an *init gadget* that activates the necessary peripherals, or a *slice gadget* that has the job of jumping into different gadgets,
but is also responsible for cleaning up registers and executing the original instruction in the firmware.

The patcher will then use the configuration created with the Ghidra Plugin and the target class to insert these gadgets into the firmware.

Read more about targets and gadgets :doc:`here <targetgadget>`.


Patching The Firmware
---------------------

When the configuration and the target class are prepared, the process of patching the firmware just comes down to executing the *flopz_instrument.py* script
that comes with the flopz installation. The script needs to be fed the configuration and target class (make sure to register your target in *all_targets.py*),
as well as the original binary and an output filename. The script will then generate the instrumented firmware by placing your shellcode into the designated locations
in the original binary.


Listeners and Protocols
------------------------

TODO
