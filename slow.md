We should be able to do this challenge with any of the binaries.

We should first disassemble the binary. Disassembly is the process of converting machine code (binary instructions which the computer understands) into a more readable form (Assembly language).

Disassembling with objdump: 

```
objdump -d slow-linux-x86_64 -M intel
```

The disassembly is divided into several sections which correspond to various sections of the original human-written program. For example, the main function is denoted by the header `00000000000011ec <main>`

We can notice several auxiliary functions added by the compiler. Aside from those functions and the main function, we see a function called `slow_add`.

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

## Main function

Once again there seems to be a for-loop. `[rbp - 72]` is being used as a loop counter. Similar to above, it is first initialized to 0 and later incremented in the loop body.

For the loop condition, the counter is compared to `[rbp - 64]`, which always holds the value of 40. So we know that the main function is looping from 0-40.

### Loop body

```
    1281: 48 8d 55 d0                  	lea	rdx, [rbp - 48]
    1285: 48 8b 45 b8                  	mov	rax, qword ptr [rbp - 72]
    1289: 48 01 d0                     	add	rax, rdx
    128c: 0f b6 00                     	movzx	eax, byte ptr [rax]
    128f: 83 f0 5a                     	xor	eax, 90
    1292: 88 45 b7                     	mov	byte ptr [rbp - 73], al
    1295: 0f b6 45 b7                  	movzx	eax, byte ptr [rbp - 73]
    1299: 89 c7                        	mov	edi, eax
    129b: e8 09 ff ff ff               	call	0x11a9 <slow_add>
    12a0: 89 c1                        	mov	ecx, eax
    12a2: 48 8b 55 c8                  	mov	rdx, qword ptr [rbp - 56]
    12a6: 48 8b 45 b8                  	mov	rax, qword ptr [rbp - 72]
    12aa: 48 01 d0                     	add	rax, rdx
    12ad: 89 ca                        	mov	edx, ecx
    12af: 88 10                        	mov	byte ptr [rax], dl
```

On the very first line the address `[rbp - 48]` is loaded into `rdx`. The value of the loop counter `[rbp - 72]` is loaded into `rax`. Then, the address that `rdx` contains is added to `rax`.

What does `[rbp - 48]` contain?

```
    1207: 48 b8 16 01 09 04 74 65 6b 3c	movabs	rax, 4353685013742027030
    1211: 48 ba 05 09 16 03 0c 04 10 16	movabs	rdx, 1589775118099679493
    121b: 48 89 45 d0                  	mov	qword ptr [rbp - 48], rax
    121f: 48 89 55 d8                  	mov	qword ptr [rbp - 40], rdx
    1223: 48 b8 01 01 07 0a 14 0e 16 05	movabs	rax, 366495898907640065
    122d: 48 ba 0a 10 0e 05 10 46 46 14	movabs	rdx, 1460932163746533386
    1237: 48 89 45 e0                  	mov	qword ptr [rbp - 32], rax
    123b: 48 89 55 e8                  	mov	qword ptr [rbp - 24], rdx
    123f: 48 b8 44 7a 16 15 79 0b 7e 32	movabs	rax, 3638358163634682436
    1249: 48 89 45 f0                  	mov	qword ptr [rbp - 16], rax
```

We notice an unusual instruction located before the call to slow_add: 

`xor eax, 90` -- Usually, it is common to xor a register with itself to clear it. It is less common to xor anything with a constant.

What does `eax` contain? 
