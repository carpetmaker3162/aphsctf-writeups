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
$$ B = 31 $$
$$ M = 2^{17} $$
$$ \text{ord}(s_i) $$ is the ASCII value of the $$ i $$-th character of the string $$ s $$

This is a simple polynomial rolling hash.
