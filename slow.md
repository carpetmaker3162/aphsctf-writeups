We should be able to do this challenge with any of the binaries.

We should first disassemble the binary. Disassembly is the process of converting machine code (binary instructions which the computer understands) into a more readable form (Assembly language).

Disassembling with objdump: 

```
objdump -d slow-linux-x86_64 -M intel
```

The disassembly is divided into several sections which correspond to various sections of the original human-written program. For example, the main function is denoted by the header `00000000000011ec <main>`

Looking at the disassembly we can notice several unusual things:

- In the main function, an unusual instruction `xor eax, 90` is seen. Usually it is very common to `xor` a register with itself to set it to 0, but it is less common to see things being `xor`'ed with constants.  
- The existence of a function called `slow_add`  
- In `slow_add`, a very large number is moved into the `rax` register (7203796438858066709)  

## slow_add

`slow_add` clearly contains a for-loop:

```
    11bd: 48 c7 45 f8 00 00 00 00      	mov	qword ptr [rbp - 8], 0
    11c5: eb 0f                        	jmp	0x11d6 <slow_add+0x2d>
    11c7: 0f b6 45 f7                  	movzx	eax, byte ptr [rbp - 9]
    11cb: 83 c0 01                     	add	eax, 1
    11ce: 88 45 f7                     	mov	byte ptr [rbp - 9], al
    11d1: 48 83 45 f8 01               	add	qword ptr [rbp - 8], 1
    11d6: 48 b8 15 eb 5b 9c b1 06 f9 63	movabs	rax, 7203796438858066709
    11e0: 48 39 45 f8                  	cmp	qword ptr [rbp - 8], rax
    11e4: 72 e1                        	jb	0x11c7 <slow_add+0x1e>
```

### Loop body

`11c7: movzx eax, byte ptr [rbp - 9]` -- this loads one byte from `[rbp - 9]` into `eax`.

`11cb: add eax, 1` -- `eax` is incremented.

`11ce: mov byte ptr [rbp - 9], al` -- The lowest byte of `eax` (`al`) is moved back into `[rbp - 9]`

Together this effectively increments `[rbp - 9]`.

### Loop counter

The memory address `[rbp - 8]` is being used as a counter variable (`i`) in the for-loop:  

`11bd: mov qword ptr [rbp - 8], 0` -- initialize counter to 0

`11d6: movabs rax, 7203796438858066709` -- load the total number of iterations into `rax`

`11e0: cmp qword ptr [rbp - 8], rax` -- compare counter to `rax`.

`11e4: jb 0x11c7` -- If counter < total, jump back to loop body.

### Conclusions about slow_add

Remember that only one byte is moved from `[rbp - 9]` into `eax`, and later only one byte is written back. Compilers also usually aligns variables by size: `[rbp - 9]` is one byte before `[rbp - 8]`. It is safe to assume that `[rbp - 9]` is a byte-sized value (such as a `char`).

Putting it all together, the program is incrementing a byte (`[rbp - 9]`) 7203796438858066709 times. On an average computer this will take years to do.

Effectively the program is doing the following:

```c
uint8_t x = 0;
for (uint64_t i = 0; i < 7203796438858066709; i++) {
    x++;
}
```

It's straightforward to optimize this, since after adding 256 times the char will wrap around. So, it is equivalent to adding 7203796438858066709 % 256 = **21** to the char.
