# Arjun
Arjun is a python script for finding hidden GET &amp; POST parameters using regex and bruteforce.

### Dependencies
- requests
- threading

### Usages
Here's how you can scan a webpage for get parameters
```
python arjun.py -u http://example.com/index.php --get
```
For POST, just use the <b>--post</b> flag.
To specify the number of threads you can use the <b>--threads</b> option as following:
```
python arjun.py -u http://example.com/index.php --get --threads 4
```
Here's a screenshot you can fap to:</br>
<img src='https://i.imgur.com/7BQv5qa.png' />

#### License
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
