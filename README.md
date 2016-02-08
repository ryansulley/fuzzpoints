# fuzzpoints

###Description
Fuzzpoints extend upon gdb's breakpoint functionality to provide security researchers another way to randomly modify memory in search of vulnerabilities. A new command is added to gdb which allows researchers to set a trigger and target location to guide memory modification. The fuzz command takes five parameters: trigger address, target address, target size, fuzz factor, and seed. The trigger address represents the point in execution where the target address and bytes within the range (specified by target size) will be modified. Fuzz factor allows the user to specify how much of the target region should be changed. Finally a seed is provided in order to help reproduce testcases.

###Install Instructions
Including the following line in your .gdbinit file
```
source ~/fuzzpoints/fuzzpoints.py
```

###Example
Lets walk through a trivial example to demonstrate usage. First lets take a very simple application to target.
```C
#include <stdio.h>

int main(int argc, char* argv[])
{
   char INPUT = 'A';
   const unsigned int loops = 100;
   unsigned int i = 0;
   for(;i<loops; ++i)
   {   
       printf("%c\n", INPUT);
   }   
   return 0;
}
```
The above code is very simple. It has a variable called INPUT which gets printed to standard out 100 times. No where in the programs original code does INPUT get modified. If we were to run this the output would resemble this:
```
A
A
A
A
...
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
   0x0000000100000f10 <+0>:     push   %rbp
   0x0000000100000f11 <+1>:     mov    %rsp,%rbp
   0x0000000100000f14 <+4>:     sub    $0x20,%rsp
   0x0000000100000f18 <+8>:     movl   $0x0,-0x4(%rbp)
   0x0000000100000f1f <+15>:    mov    %edi,-0x8(%rbp)
   0x0000000100000f22 <+18>:    mov    %rsi,-0x10(%rbp)
   0x0000000100000f26 <+22>:    movb   $0x41,-0x11(%rbp)
   0x0000000100000f2a <+26>:    movl   $0x64,-0x18(%rbp)
   0x0000000100000f31 <+33>:    movl   $0x0,-0x1c(%rbp)
   0x0000000100000f38 <+40>:    cmpl   $0x64,-0x1c(%rbp)
   0x0000000100000f3f <+47>:    jae    0x100000f6a <main+90>
   0x0000000100000f45 <+53>:    lea    0x46(%rip),%rdi        # 0x100000f92
   0x0000000100000f4c <+60>:    movsbl -0x11(%rbp),%esi
   0x0000000100000f50 <+64>:    mov    $0x0,%al
   0x0000000100000f52 <+66>:    callq  0x100000f72
   0x0000000100000f57 <+71>:    mov    %eax,-0x20(%rbp)
   0x0000000100000f5a <+74>:    mov    -0x1c(%rbp),%eax
   0x0000000100000f5d <+77>:    add    $0x1,%eax
   0x0000000100000f62 <+82>:    mov    %eax,-0x1c(%rbp)
   0x0000000100000f65 <+85>:    jmpq   0x100000f38 <main+40>
   0x0000000100000f6a <+90>:    xor    %eax,%eax
   0x0000000100000f6c <+92>:    add    $0x20,%rsp
   0x0000000100000f70 <+96>:    pop    %rbp
   0x0000000100000f71 <+97>:    retq   
End of assembler dump.
(gdb) 
```
We can see the printf call is happening at location 0x100000f52. This would be a great place to put our fuzzpoint at but now we need a target location and size. We can do this a number of ways. For binaries with debug symbols present, we can utilize gdb and use the &INPUT argument to specify the address of the target variable. However if these symbols aren't present, we can see the value 0x41 is placed at $rbp-0x11. Since this is just a single byte we want to modify, we know the size is 1 byte. Now lets construct our fuzzpoint.
```
(gdb) fuzz *main+66 &INPUT 1 0.001 500
Breakpoint 1 at 0x100000f52: file test.c, line 10.
```
We are setting the factor to 0.001 but since the number of bits is so limited this will produce only one modification. The seed can be set to any numeric value and in this case is 500. Now we just run the program to get the following output:
```
A
Q

?


?
?
?
?
?
4








<
|
x
z
r
b
B
J
K





?
?


S
R
r
v
V
^
N
L
```
Notice how the program on each iteration is modifying the value stored at &INPUT.

