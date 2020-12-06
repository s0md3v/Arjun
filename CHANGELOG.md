#### 2.0-beta
- Added an anamoly detection algorithm with 9 factors
- Added a HTTP response analyzer for handling errors and retrying requests
- Significantly improved heuristic scanner
- `--passive` option for collecting parameters from otx, commoncrawl and archive.org
- `-c` option to define number of parameters to be sent at once
- import via `-i` options now supports: BurpSuite log, raw request file, text file with urls
- `-T` option to specify HTTP connection timeout
- combined `-m` option for specifiying HTTP request method
- Various bug fixes and better output

#### 1.6
- `--stable` switch for handling rate limits
- Include empty JS variables for testing
- Various optimizations and bug fixes
- Handle keyboard interruption
- Removed redundant code

#### 1.5
- Ignore dynamic content
- Detect int-only parameters
- Include URL in json output
- Track each reflection separately
- Improved error handling

#### 1.4
- Added `JSON` support
- Fixed a major bug in detection logic
- `-o` option to save result to a file
- `--urls` option to scan list of URLs
- Ability to supply HTTP headers from CLI

#### 1.3
- improved logic
- detection by plain-text content matching
- `--include` switch to include persistent data
- fixed a bug that caused user supplied HTTP headers to have no effect

#### 1.2-beta
- Drastic performance improvement (x50 faster)

#### 1.1
Initial stable release
