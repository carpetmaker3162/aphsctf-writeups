## Hints  

Hint 1: the intended solution does not exploit any of the session management code

Hint 2: can we exploit the randomness of the program?

## Intended Solution  

(1/100)^5 = one in 10 billion, so it's not feasible to bruteforce. 

How does the server check the user's guesses against the correct number? Looking at the code, it makes a POST request to `/api/guess`, which generates a random number on the spot using `/api/random`. In other words the correct number is generated AFTER the user makes a guess, instead of pre-generating it, so we can't really trivially know the correct number beforehand (afaik)

`/api/random` seems to grab a user-specific "rng state" then generates a random number with it. Specifically it uses the `Random` class (`lib/random.ts`).

The `Random` class is meant to emulate `Math.random()`. I had to write this class so that each user can have their own rng instance, which `Math.random()` doesn't support. 

`Math.random()` is commonly implemented with the xorshift128+ algorithm*. This algorithm is not secure, and is easily predictable. 

xorshift128+ has a 128-bit internal state, in the form of two 64-bit integers. Given several outputs of the algorithm, it is possible to solve for the internal state and thus predict future outputs. 

#### How prediction works  

How to solve for the internal state? We do some math. To explain how, let's use a very simple (and very bad) rng as an example: our rng will have only one state and will generate integers from 0-9. On each iteration of the rng, the new state is `(prevState + 13) modulo 10`, and the rng returns the new state as an output. This is repeated for future iterations. 

Let's say our rng outputs the number 8. Let $$\( x \)$$ be the rng's state right before generating 8. We can then establish an equation:

$$(x + 13) \mod 10 = 8$$

A solution for this can then be found easily ($$x = 5$$). We can then keep applying this operation to predict future outputs of the rng. Since our rng only had one state, had a very simple transition from one state to the next, and had a very short period (10), we only needed one output from the rng in order to be able to make correct predictions.

The math in xorshift128 is a bit more complicated. Let $$s_0$$ and $$s_1$$ be the current 64-bit states. The new $$s_0$$ and $$s_1$$ are calculated as follows:

$$
x = s_0
$$

$$
y = s_1
$$

$$
s_0 = y
$$

$$
x = x \oplus (x \ll 23)
$$

$$
s_1 = x \oplus y \oplus (x \gg 17) \oplus (y \gg 26)
$$

The rng then outputs $$s_0$$.

#### Z3  

Luckily, we don't need to do too much math ourselves. Z3 is a theorem prover which can also solve symbolic logic. We can treat the equations derived from the outputs of the prng as constraints, and solve for the unknown state values using Z3. 

Here's an example program to solve for future outputs given past outputs of V8's `Math.random()`. I wont go into too many implementation details but if you are interested it involves an interesting rabbit hole about how floating point numbers are represented (IEEE 754). 

```
(link program here)
```

#### Beating the genie  

The client is allowed to call the `/api/random` API using `fetch`. You can call the API from the console a few times to get a few prng outputs from the server, then use them to predict future outputs using Z3. 

The last step is to notice that regardless of whether the user guesses correctly or not, the server makes an additional call to `/api/random` to choose a random message to display to the user. This call causes the prng to advance forward a state. So, after solving for future outputs you should use every other prediction to make a guess. 

#### Takeaways  

Avoid relying on prngs (pseudorandom number generators) for secure random number generation. This include JavaScript's `Math.random()` and Python's `random.random()`. They are decently uniform prngs for day-to-day applications, but should not be used for things like cryptography. 

Secure sources of randomness include `/dev/urandom`, which is considered secure enough for cryptographic purposes.

#### Note

*Our `Random` class specifically emulates how `Math.random()` is implemented in Google Chrome and Microsoft Edge. Depending on your browser, the implementation of `Math.random()` may have slight variations, but the underlying algorithm is the same. Regardless, this CTF is equally doable regardless of which browser you are using.

I don't know the exact details of the `Math.random()` implementation in the V8 engine. V8 seems to use the normal (not reverse) xorshift128+ algorithm, and then I also found some descriptions online of it popping outputs in LIFO (last in first out) order... etc. If someone can figure out the details of how V8 implements `Math.random()` I'd be very glad to know (please do reach  out).