# fuzzpoints
In-memory fuzzing for GDB
=========================
Fuzzing is a very well known technique for security researchers to find vulnerabilities in software. In general, this just means supplying a program with slightly invalid input in order to see if the code handles these conditions correctly.
Depending on how a given program accepts input this can range from compiling a set of invalid files, command line arguments, or sending malformed packets. However there are some situations that make generating these input values difficult.
If the given program decrypts these inputs before processing, creating such targeted inputs will be difficult and may require reversing a complex crypto algorithm. Here is were in-memory fuzzers come into play.
Traditionally in-memory fuzzers are built using function hooks which act as replacements for known functions and modify input either upon entering the function or returning fuzzed output to be processed later. This can be a hassle to setup.
Fuzzpoints utilizes gdb and breakpoint functionality to construct a tool to target a given range of addresses and when execution reaches a specified location, mutate that range of values.
