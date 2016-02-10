# fuzzpoints

### Description
Fuzzpoints extend upon gdb's breakpoint functionality to provide security researchers another way to randomly modify memory in search of vulnerabilities. A new command, called fuzz, is added to gdb which allows researchers to set a trigger and target location to guide memory modification. The fuzz command takes five parameters: trigger address, target address, target size, fuzz factor, and seed.

### TODO: Options with example usage

### Install Instructions
Including the following line in your .gdbinit file
```bash
source ~/fuzzpoints/fuzzpoints.py
```

### Example
Lets walk through a trivial example to demonstrate usage. First lets take a very simple application to target.
```C
#include <stdio.h>

int main(int argc, char* argv[])
{
   char INPUT[] = "i will not forget to check the bounds of user input";
   const unsigned int loops = 10;
   unsigned int i = 0;
   for(;i<loops; ++i)
   {   
       printf("%s\n", INPUT);
   }   
   return 0;
}
```
The above code is very simple. It has a variable called ```INPUT``` which gets printed to standard out 10 times. Nowhere in the program's original code does ```INPUT``` get modified. If we were to run this the output would resemble this:
```
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
i will not forget to check the bounds of user input
```
Now lets load this program in gdb and disassemble the main function:
```
GNU gdb (GDB) 7.10.1
Copyright (C) 2015 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-apple-darwin15.2.0".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
<http://www.gnu.org/software/gdb/documentation/>.
For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from ./a.out...Reading symbols from /Users/ryansullivan/a.out.dSYM/Contents/Resources/DWARF/a.out...done.
done.
(gdb) disassemble main
Dump of assembler code for function main:
   0x0000000100000e70 <+0>:     push   %rbp
   0x0000000100000e71 <+1>:     mov    %rsp,%rbp
   0x0000000100000e74 <+4>:     sub    $0x60,%rsp
   0x0000000100000e78 <+8>:     lea    0xe1(%rip),%rax        # 0x100000f60
   0x0000000100000e7f <+15>:    mov    $0x34,%ecx
   0x0000000100000e84 <+20>:    mov    %ecx,%edx
   0x0000000100000e86 <+22>:    lea    -0x40(%rbp),%r8
   0x0000000100000e8a <+26>:    mov    0x17f(%rip),%r9        # 0x100001010
   0x0000000100000e91 <+33>:    mov    (%r9),%r9
   0x0000000100000e94 <+36>:    mov    %r9,-0x8(%rbp)
   0x0000000100000e98 <+40>:    movl   $0x0,-0x44(%rbp)
   0x0000000100000e9f <+47>:    mov    %edi,-0x48(%rbp)
   0x0000000100000ea2 <+50>:    mov    %rsi,-0x50(%rbp)
   0x0000000100000ea6 <+54>:    mov    %r8,%rdi
   0x0000000100000ea9 <+57>:    mov    %rax,%rsi
   0x0000000100000eac <+60>:    callq  0x100000f18
   0x0000000100000eb1 <+65>:    movl   $0xa,-0x54(%rbp)
   0x0000000100000eb8 <+72>:    movl   $0x0,-0x58(%rbp)
   0x0000000100000ebf <+79>:    cmpl   $0xa,-0x58(%rbp)
   0x0000000100000ec6 <+86>:    jae    0x100000ef1 <main+129>
   0x0000000100000ecc <+92>:    lea    0xc1(%rip),%rdi        # 0x100000f94
   0x0000000100000ed3 <+99>:    lea    -0x40(%rbp),%rsi
   0x0000000100000ed7 <+103>:   mov    $0x0,%al
   0x0000000100000ed9 <+105>:   callq  0x100000f1e
   0x0000000100000ede <+110>:   mov    %eax,-0x5c(%rbp)
   0x0000000100000ee1 <+113>:   mov    -0x58(%rbp),%eax
   0x0000000100000ee4 <+116>:   add    $0x1,%eax
   0x0000000100000ee9 <+121>:   mov    %eax,-0x58(%rbp)
   0x0000000100000eec <+124>:   jmpq   0x100000ebf <main+79>
   0x0000000100000ef1 <+129>:   mov    0x118(%rip),%rax        # 0x100001010
   0x0000000100000ef8 <+136>:   mov    (%rax),%rax
   0x0000000100000efb <+139>:   cmp    -0x8(%rbp),%rax
   0x0000000100000eff <+143>:   jne    0x100000f0d <main+157>
   0x0000000100000f05 <+149>:   xor    %eax,%eax
   0x0000000100000f07 <+151>:   add    $0x60,%rsp
   0x0000000100000f0b <+155>:   pop    %rbp
   0x0000000100000f0c <+156>:   retq   
   0x0000000100000f0d <+157>:   callq  0x100000f12
End of assembler dump.
(gdb)

```
We can see the ```printf``` call is happening at location main+105. This would be a great place to put our fuzzpoint's trigger address. Now we need to determine what to set for our target address. We can do this a number of ways. For binaries with debug symbols present, we can utilize gdb and use the variable name from source code; in this case it's ```INPUT```. If these symbols aren't present, however, you can supply an address instead. To determine the size of our buffer, we can again utilize gdb's support for the sizeof function. In this example we only want to flip 1% of the bits in our buffer. The seed is provided in order to reproduce the results. The example command that we want to run for our scenario is shown below.
```
(gdb) fuzz *main+105 INPUT sizeof(INPUT) 0.01 500
Breakpoint 1 at 0x100000f52: file test.c, line 10.
```
Now we just run the program to get the following output:
```
(gdb) run
Starting program: /Users/ryansullivan/a.out
I will noforget to checj the bounds of user inpuv
I will nmforget to checj thm bounds of e3er inpuv
A will nmforget to checj thm bound3`of e3er ijpuv
A will nmforget0to
C will nm? fobget0to
B will nm? fobcet0to
B will nm? fobcet0po
B will nm? Fobcet0po
B will nm? Fobcet0po
B will nm? FObcet0po
[Inferior 1 (process 10108) exited normally]
```
Notice how the program on each iteration is modifying the value stored at ```INPUT```.
