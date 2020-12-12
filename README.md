
<h1 align="center">
  <br>
  <a href="https://github.com/s0md3v/Arjun"><img src="https://image.ibb.co/c618nq/arjun.png" alt="Arjun"></a>
  <br>
  Arjun
  <br>
</h1>

<h4 align="center">HTTP Parameter Discovery Suite</h4>

<p align="center">
  <a href="https://github.com/s0md3v/Arjun/releases">
    <img src="https://img.shields.io/github/release/s0md3v/Arjun.svg">
  </a>
  <a href="https://github.com/s0md3v/Arjun/issues?q=is%3Aissue+is%3Aclosed">
      <img src="https://img.shields.io/github/issues-closed-raw/s0md3v/Arjun.svg">
  </a>
</p>

![demo](https://i.ibb.co/q5F8qPY/Screenshot-2020-12-06-21-54-52.png)

### What's Arjun?

Arjun can find query parameters for URL enpoints. If you don't get what that means, it's okay, read along.

Web applications use parameters (or queries) to accept user input, take the following example into consideration

`http://api.example.com/v1/userinfo?id=751634589`

This URL seems to load user information for a specific user id, but what if there exists a parameter named `admin` which when set to `True` makes the endpoint provide more information about the user?\
This is what Arjun does, it finds valid HTTP parameters with a huge default dictionary of 25,980 parameter names.

The best part? It takes less than 20 seconds to go through this huge list while making just 50-60 requests to the target. [Here's how](https://github.com/s0md3v/Arjun/wiki/How-Arjun-works%3F).

### Why Arjun?

- Anomaly detection with 9 factors
- Supports `GET/POST/POST-JSON`
- Automatically handles rate limits and timeouts
- Can import targets from BurpSuite, text file or a raw request file
- Can passively extract parameters from JS or 3 external sources
- Makes ~50 requests in 20 seconds for checking 25,980 parameter names

### How to use Arjun?

> **Note:** Arjun doesn't work with python < 3.4

A detailed usage guide is available on [Usage](https://github.com/s0md3v/Arjun/wiki/Usage) section of the Wiki.

Direct links to some basic options are given below:

- [Scan a single URL](https://github.com/s0md3v/Arjun/wiki/Usage#scan-a-single-url)
- [Import multiple targets](https://github.com/s0md3v/Arjun/wiki/Usage#import-multiple-targets)
- [Save output to a file](https://github.com/s0md3v/Arjun/wiki/Usage#save-output-to-a-file)
- [Use custom HTTP headers](https://github.com/s0md3v/Arjun/wiki/Usage#use-custom-http-headers)

Optionally, you can use the `--help` argument to explore Arjun on your own.

##### Credits
The parameter names wordlist is taken from [@SecLists](https://github.com/danielmiessler/SecLists).
