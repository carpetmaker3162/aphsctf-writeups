## patrick1  

The flag is hidden in the metadata of the png file. A file's metadata provides additional information about the file, such as its size, when it was created, and its modification dates. 

You can view metadata by using a [metadata viewer tool](https://www.metadata2go.com/) or by simply opening the image using a text editor.

## patrick2

The folder is a git repository: you can tell by the presence of the `.git/` folder. Git is a very common tool for version control, tracking past versions of files among other things.

Running the `git reflog` command reveals that there have been commits made to now deleted branches. After looking around for a bit you will find that `d27f025` is the commit that contains the flag. Move to that branch by running `git checkout d27f025`. The flag is again encoded in the metadata of the image in Base64.

Alternatively, you could have encoded "aphsCTF" in Base64 and then used `grep` to search for occurrences in the `.git/` folder, but this required a lot more guessing.

## cookies

Cookies are data that a website stores on your browser/your computer to remember information about past sessions. 

On our site, you may notice that if you decline cookies then reload, the cookie prompt reappears. If you accept cookies, it will not appear again.

You can view cookies by going into your browser's devtools ("Inspect Element") and heading to the Application tab. You can then view a list of cookies as key-value pairs.

The flag is in a cookie, encoded in Base64.

## ROT13

Rot13 is a simple cipher that replaces every letter with the 13th letter after it in the alphabet.

There are numerous online websites that can be used to encode/decode Rot13.
