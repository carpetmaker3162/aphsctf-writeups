Taking this step by step, the admin panel checks your password using this block of code:

```py
if secure_hash(password) == password_hashes[username]:
    return render_template(
        'index.html',
        message='Access Granted',
        flag=flag,
        username=username
    )
```

`password_hashes` originates from the file `static/passwords.json`:

```
with open('static/passwords.json') as file:
    password_hashes = json.load(file)
```

Its contents are:

```
{"admin": 56951}
```

The username we are supposed to use is evidently "admin". 56951 however is NOT the password but rather the hash of the password.

A hash function (or more specifically in this case a key derivation function) is a function that takes in an input (such as a password) and deterministically produces a fixed-length output (a "hash value"). They are designed such that if you only have the hash value, it is difficult to reconstruct an input which produces that hash value.

Services which require you to use a password do not store your password, but rather store the password's hash value. When you enter a password to authenticate yourself, your input is hashed and compared against the "correct" hash value in the service's database.

For this challenge our hash function is `secure_hash`, whose name is misleading because it is not secure at all. Here is its implementation:

```
B = 31
M = 2**17

def secure_hash(s):
    hash_val = 0

    for i, c in enumerate(s):
        hash_val = (hash_val + ord(c) * B**i) % M

    return hash_val
```

This is a simple polynomial rolling hash defined as

$$
\text{hash}(s) = (\text{ord}(s_0) \cdot B^0 + \text{ord}(s_1) \cdot B^1 + \text{ord}(s_2) \cdot B^2 + \ldots + \text{ord}(s_{n-1}) \cdot B^{n-1}) \mod M
$$

Where:
- B = 31
- M = 2^17
- ord(s_i) refers to the ASCII value of the i-th character of the string

In other words, when you start with a certain password, increasing the ASCII value of the first character by 1 will increase the value of the hash by 31^0 = **1**. Increasing the ASCII of the 2nd char will increase the value of the hash by 31^1 = **31**, and so on.

You can manually solve this by playing around with different strings. Alternatively I used chatgpt to write a script that cracks a hash value with arbitrary values for B and M, which uses backtracking. (too lazy to write myself)

"ab8" is a valid password that produces the hash value 56951. 

This was not the original password I used; since the hash mods the hash value by 2^17 there are an infinite number of possible passwords which produce this hash. This is what is called a hash collision.

## Takeaways

Avoid writing your own key derivation function for passwords. Currently the common key derivation functions used in industry include PBKDF2, bcrypt, Argon2, etc. These have the property of intentionally being computationally expensive (slow to compute), which helps resist against brute-force attacks.
