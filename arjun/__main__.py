"""The main part of Arjun."""
import argparse
import concurrent.futures
import json
import os

from arjun.const import BANNER
from arjun.core.bruteforcer import brute_force, quick_brute_force
from arjun.core.colors import bad, end, good, green, info, run
from arjun.core.prompt import prompt
from arjun.core.requester import requester
from arjun.core.utils import (
    extract_headers, extract_value, get_params, heuristic, narrower,
    random_string, remove_tags, slicer, stabilize)


def main():
    """Run Arjun."""

    print(BANNER)

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="target URL", dest="url")
    parser.add_argument("-d", help="request delay", dest="delay", type=int)
    parser.add_argument(
        "-t", help="number of threads", dest="threads", type=int
    )
    parser.add_argument(
        "-f", help="path to parameter file", dest="parameters_file"
    )
    parser.add_argument(
        "-o", help="path for the output file", dest="output_file"
    )
    parser.add_argument(
        "--get", help="use GET method", dest="get", action="store_true"
    )
    parser.add_argument(
        "--post", help="use POST method", dest="post", action="store_true"
    )
    parser.add_argument(
        "--headers",
        help="HTTP headers prompt",
        dest="headers",
        action="store_true",
    )
    parser.add_argument(
        "--include", help="include this data in every request", dest="include"
    )

    args = parser.parse_args()

    url = args.url
    parameters_file = args.parameters_file or "{}{}".format(
        os.getcwd(), "/arjun/db/params.txt"
    )
    headers = args.headers
    delay = args.delay or 0
    include = args.include or {}
    thread_count = args.threads or 2

    if headers:
        headers = extract_headers(prompt())
    else:
        headers = {}

    if args.get:
        get = True
    else:
        get = False

    include = get_params(include)

    param_list = []
    try:
        with open(parameters_file, "r") as params_file:
            for line in params_file:
                param_list.append(line.strip("\n"))
    except FileNotFoundError:
        print("%s The specified file doesn't exist" % bad)
        quit()

    url = stabilize(url)

    print("%s Analysing the content of the web page" % run)
    first_response = requester(url, include, headers, get, delay)

    print(
        "%s Now let's see how the target deals with a non-existent parameter"
        % run
    )

    original_fuzz = random_string(6)
    data = {original_fuzz: original_fuzz[::-1]}
    data.update(include)
    response = requester(url, data, headers, get, delay)
    reflections = response.text.count(original_fuzz[::-1])
    print("%s Reflections: %s%i%s" % (info, green, reflections, end))

    original_response = response.text
    original_code = response.status_code
    print("%s Response code: %s%i%s" % (info, green, original_code, end))

    new_length = len(response.text)
    plain_text = remove_tags(original_response)
    plain_text_length = len(plain_text)
    print("%s Content length: %s%i%s" % (info, green, new_length, end))
    print(
        "%s Plain-text length: %s%i%s" % (info, green, plain_text_length, end)
    )

    factors = {"same_html": False, "same_plain_text": False}
    if len(first_response.text) == len(original_response):
        factors["same_html"] = True
    elif len(remove_tags(first_response.text)) == len(plain_text):
        factors["same_plain_text"] = True

    print("%s Parsing web page for potential parameters" % run)
    heuristic(first_response.text, param_list)

    fuzz = random_string(8)
    data = {fuzz: fuzz[::-1]}
    data.update(include)

    print("%s Performing heuristic level checks" % run)

    to_check = slicer(param_list, 25)
    found_params = []
    while True:
        to_check = narrower(
            quick_brute_force,
            original_response,
            original_code,
            factors,
            include,
            delay,
            headers,
            url,
            get,
            to_check,
            thread_count,
        )
        to_check = extract_value(to_check, found_params)
        if not to_check:
            break

    if found_params:
        print(
            "%s Heuristic found %i potential parameters"
            % (info, len(found_params))
        )
        param_list = found_params

    final_result = []
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
        )
        for param in found_params
    )
    for i, result in enumerate(concurrent.futures.as_completed(futures)):
        if result.result():
            final_result.append(result.result())
        print("%s Progress: %i/%i" % (info, i + 1, len(param_list)), end="\r")
    print("%s Scan completed" % info)

    for each in final_result:
        for param, reason in each.items():
            print(
                "%s Valid parameter found: %s%s%s" % (good, green, param, end)
            )
            print("%s Reason: %s" % (info, reason))
            json_result.append({"param": param, "reason": reason})

    # Finally, export to JSON
    if args.output_file and json_result:
        print("%s Saving output to JSON file in %s" % (info, args.output_file))
        with open(str(args.output_file), "w") as json_output:
            json.dump(
                {"results": json_result}, json_output, sort_keys=True, indent=4
            )
