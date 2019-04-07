
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

![demo](https://i.ibb.co/n0XdvZW/Screenshot-2019-04-07-20-08-04.png)

### Features
- Multi-threading
- 4 modes of detection
- A typical scan takes 30 seconds
- Regex powered heuristic scanning
- Huge list of 25,980 parameter names
- Makes just 30-35 requests to the target

### Usage

> **Note:** Arjun doesn't work with python < 3.4

#### Discover parameters

To find `GET` parameters, you can simply do:

`python3 arjun.py -u https://api.example.com/endpoint --get`

Similarly, use `--post` to find `POST` parameters.

#### Multi-threading
Arjun uses 2 threads by default but you can tune its performance according to your network connection.

`python3 arjun.py -u https://api.example.com/endpoint --get -t 22`

#### Delay between requests
You can delay the request by using the `-d` option as follows:

`python3 arjun.py  -u https://api.example.com/endpoint --get -d 2`

#### Including presistent data
Let's say you have an API key that you need to send with every request, to tell Arjun to do that you can use the `--include` option as follows:

`python3 arjun.py  -u https://api.example.com/endpoint --get --include 'api_key=xxxxx'`

OR

`python3 arjun.py  -u https://api.example.com/endpoint --get --include '{"api_key":"xxxxx"}'`

To include multiple parameters, use `&` to seperate them or pass them as a valid json object.

#### JSON Output
You can save the result in a JSON format by using the `-o` as follows:

`python3 arjun.py -u https://api.example.com/endpoint --get -o result.json`

#### Adding HTTP Headers
Using the `--headers` switch will open an interactive prompt where you can paste your headers. Press `Ctrl + S` to save and `Ctrl + X` to procced.

![headers](https://image.ibb.co/jw5NgV/Screenshot-2018-10-27-18-45-32.png)

> **Note:** Arjun uses `nano` as the default editor for the prompt but you can change it by tweaking `/core/prompt.py`.

##### Credits
The parameter names are taken from [@SecLists](https://github.com/danielmiessler/SecLists).
