"""The main part of Arjun."""
import argparse
import concurrent.futures
import json
import os

from arjun.const import BANNER
from arjun.core.bruteforcer import brute_force, quick_brute_force
from arjun.core.colors import bad, end, good, green, info, run
from arjun.core.config import global_variables as user_variables
from arjun.core.prompt import prompt
from arjun.core.requester import requester
from arjun.core.utils import (
    extract_headers, extract_value, get_params, heuristic, log, narrower,
    random_string, remove_tags, slicer, stabilize)

try:
    import concurrent.futures
except ImportError:
    print("%s Please use Python > 3.4 to run Arjun." % bad)
    quit()


def main():
    """Run Arjun."""
    print(BANNER)

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="target URL", dest="url")
    parser.add_argument("-f", help="wordlist path", dest="wordlist")
    parser.add_argument("-d", help="request delay", dest="delay", type=int)
    parser.add_argument(
        "-t", help="number of threads", dest="threads", type=int
    )
    parser.add_argument(
        "-o", help="path for the output file", dest="output_file"
    )
    parser.add_argument("--urls", help="file containing URLs", dest="url_file")
    parser.add_argument(
        "--get", help="use GET method", dest="get", action="store_true"
    )
    parser.add_argument(
        "--post", help="use POST method", dest="post", action="store_true"
    )
    parser.add_argument(
        "--include", help="include this data in every request", dest="include"
    )
    parser.add_argument(
        "--headers",
        help="add HTTP headers",
        dest="headers",
        nargs="?",
        const=True,
    )
    parser.add_argument(
        "--json",
        help="treat POST data as JSON",
        dest="json_data",
        action="store_true",
    )
    args = parser.parse_args()

    url = args.url
    json_data = args.json_data
    headers = args.headers
    delay = args.delay or 0
    url_file = args.url_file
    include = args.include or {}
    thread_count = args.threads or 2
    wordlist = args.wordlist or "{}/{}".format(
        os.path.dirname(os.path.realpath(__file__)), "db/params.txt"
    )
    global_variables = vars(args)
    global_variables.update(user_variables)
    variables = global_variables

    if type(headers) == bool:
        headers = extract_headers(prompt())
    elif type(headers) == str:
        headers = extract_headers(headers)
    else:
        headers = {}

    if json_data:
        headers["Content-type"] = "application/json"

    if args.get:
        get = True
    else:
        get = False

    include = get_params(include)

    param_list = []
    try:
        with open(wordlist, "r") as file:
            for line in file:
                param_list.append(line.strip("\n"))
    except FileNotFoundError:
        log(
            "%s The specified file for parameters doesn't exist" % bad,
            variables=variables,
        )
        quit()

    urls = []

    if url_file:
        try:
            with open(url_file, "r") as file:
                for line in file:
                    urls.append(line.strip("\n"))
        except FileNotFoundError:
            log(
                "%s The specified file for URLs doesn't exist" % bad,
                variables=variables,
            )
            quit()

    if not url and not url_file:
        log("%s No URL specified" % bad)
        quit()

    def perform_test(
        url, include, headers, get, delay, param_list, thread_count, variables
    ):
        """Perform the tests."""
        url = stabilize(url)

        log("%s Analysing the content of the webpage" % run, variables)
        first_response = requester(
            url, include, headers, get, delay, variables
        )

        log(
            '%s Analysing behaviour for a non-existent parameter' % run,
            variables=variables,
        )

        original_fuzz = random_string(6)
        data = {original_fuzz: original_fuzz[::-1]}
        data.update(include)
        response = requester(url, data, headers, get, delay, variables)
        reflections = response.text.count(original_fuzz[::-1])
        log(
            "%s Reflections: %s%i%s" % (info, green, reflections, end),
            variables=variables,
        )

        original_response = response.text
        original_code = response.status_code
        log(
            "%s Response Code: %s%i%s" % (info, green, original_code, end),
            variables=variables,
        )

        new_length = len(response.text)
        plain_text = remove_tags(original_response)
        plain_text_length = len(plain_text)
        log(
            "%s Content Length: %s%i%s" % (info, green, new_length, end),
            variables=variables,
        )
        log(
            "%s Plain-text Length: %s%i%s"
            % (info, green, plain_text_length, end),
            variables=variables,
        )

        factors = {"same_html": False, "same_plain_text": False}
        if len(first_response.text) == len(original_response):
            factors["same_html"] = True
        elif len(remove_tags(first_response.text)) == len(plain_text):
            factors["same_plain_text"] = True

        log(
            "%s Parsing webpage for potential parameters" % run,
            variables=variables,
        )
        heuristic(first_response.text, param_list)

        fuzz = random_string(8)
        data = {fuzz: fuzz[::-1]}
        data.update(include)

        log("%s Performing heuristic level checks" % run, variables=variables)

        to_check = slicer(param_list, 50)
        found_params = []
        while True:
            to_check = narrower(
                quick_brute_force,
                to_check,
                url,
                include,
                headers,
                get,
                delay,
                original_response,
                original_code,
                reflections,
                factors,
                thread_count,
                variables,
            )
            to_check = extract_value(to_check, found_params)
            if not to_check:
                break

        if found_params:
            log(
                "%s Heuristic found %i potential parameters"
                % (info, len(found_params)),
                variables=variables,
            )
            param_list = found_params

        test_result = []
        json_result = []

        threadpool = concurrent.futures.ThreadPoolExecutor(
            max_workers=thread_count
        )
        futures = (
            threadpool.submit(
                brute_force,
                param,
                original_response,
                original_code,
                factors,
                include,
                reflections,
                delay,
                headers,
                url,
                get,
                variables,
            )
            for param in found_params
        )
        for index, result in enumerate(
            concurrent.futures.as_completed(futures)
        ):
            if result.result():
                test_result.append(result.result())
            log(
                "%s Progress: %i/%i" % (info, index + 1, len(param_list)),
                mode="run",
                variables=variables,
            )

        log("%s Scan completed" % info)

        for each in test_result:
            for param, reason in each.items():
                log(
                    "%s Valid parameter found: %s%s%s"
                    % (good, green, param, end),
                    variables=variables,
                )
                log("%s Reason: %s" % (info, reason), variables=variables)
                json_result.append({"param": param, "reason": reason})
        if not json_result:
            log(
                "%s Unable to verify existence of parameters detected by "
                "heuristic" % bad,
                variables=variables,
            )

        return json_result

    final_result = []

    if url:
        final_result = perform_test(
            url,
            include,
            headers,
            get,
            delay,
            param_list,
            thread_count,
            variables,
        )
    elif urls:
        final_result = {}
        for url in urls:
            log("%s Scanning: %s" % (run, url), variables=variables)
            json_result = perform_test(
                url,
                include,
                headers,
                get,
                delay,
                list(param_list),
                thread_count,
                variables,
            )
            if json_result:
                log(
                    "%s Parameters found: %s"
                    % (
                        good,
                        ", ".join([each["param"] for each in json_result]),
                    ),
                    variables=variables,
                )
            final_result[url] = json_result

    # Finally, export to JSON
    if args.output_file and final_result:
        log(
            "%s Saving output to JSON file in %s" % (info, args.output_file),
            variables=variables,
        )
        with open(str(args.output_file), "w+") as json_output:
            json.dump(
                {"results": final_result},
                json_output,
                sort_keys=True,
                indent=4,
            )


if __name__ == "__main__":
    main()
