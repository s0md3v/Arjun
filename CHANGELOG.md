#### 2.2.6
- Fixed Arjun getting infinitely stuck on some webpages

#### 2.2.5
- Skip scanning of non-webpage urls
- Various bug fixes

#### 2.2.2
- Probing improvements
- Fix "target is misbehaving" errors
- Variable chunk size depending on HTTP method
- Improved heuristics
- Allow up to 20 "server fault" errors

#### 2.2.0
- Ability to detect parameters that respond to a certain value e.g. "?debug=yes"
- Added "required parameter" detection 
- Heuristic can now extract words out of json/text responses
- Fixed -oB option description

#### 2.1.6
- Fixed multiple breaking bugs
- Export results as they come in multi-target mode
- Various improvements to output in multi-target mode
- changed default chunk size 300->500 and threads to 2->5

#### 2.1.5
- Fixed header comparison (will fix infinite bruteforce on some targets)
- Fixed catastrophic backtracking in some regexes (arjun used to get stuck)
- New logic for handling redirections
- `--disable-redirects` option

#### 2.1.4
- Fixed file-paths not being windows compatible
- Fixed and improved JavaScript heuristics scanning
- Fixed missing ampersands in `-oT` output
- Refactoring of help options and code

#### 2.1.3
- Fixed memory exhaustion bug
- Fixed parsing of raw HTTP files
- Added new detection factor: `number of lines`
- Failed retries are now handled properly

#### 2.1.2
- Minor code cleanup
- Fixed `--headers` option

#### 2.1.1
- Fixed circular import
- Fixed BurpSuite export
- Fixed not working headers
- Better response type checking
- Fixed wordlist error on Windows
- Fixed `Content-Type` header bug

#### 2.1.0
- Added `XML` method
- `-q` option for quiet mode
- New wordlists backed by research
- `-oT` option for txt export
- `-oB` option for BurpSuite export
- `-oJ` alias for JSON export
- Added support for custom injection point in `XML` and `JSON`
- pypi package

#### 2.0-beta
- Added an anomaly detection algorithm with 9 factors
- Added a HTTP response analyzer for handling errors and retrying requests
- Significantly improved heuristic scanner
- `--passive` option for collecting parameters from otx, commoncrawl and archive.org
- `-c` option to define number of parameters to be sent at once
- import via `-i` options now supports: BurpSuite log, raw request file, text file with urls
- `-T` option to specify HTTP connection timeout
- combined `-m` option for specifying HTTP request method
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
