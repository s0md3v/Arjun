"""Helpers for Arjun."""
import concurrent.futures
import json
import random
import re
import string

import requests

from arjun.core.colors import bad, end, good, green, info


def narrower(
    brute_forcer,
    original_response,
    original_code,
    factors,
    include,
    delay,
    headers,
    url,
    get,
    old_param_list,
    thread_count,
):
    """Narrow the parameters."""
    new_param_list = []
    potential_parameters = 0
    threadpool = concurrent.futures.ThreadPoolExecutor(
        max_workers=thread_count
    )
    futures = (
        threadpool.submit(
            brute_forcer,
            part,
            original_response,
            original_code,
            factors,
            include,
            delay,
            headers,
            url,
            get,
        )
        for part in old_param_list
    )
    for data, result in enumerate(concurrent.futures.as_completed(futures)):
        if result.result():
            potential_parameters += 1
            new_param_list.extend(slicer(result.result()))
        print(
            "%s Processing: %i/%-6i" % (info, data + 1, len(old_param_list)),
            end="\r",
        )
    return new_param_list


def extract_headers(headers):
    """Extract the HTTP headers."""
    sorted_headers = {}
    matches = re.findall(r"(.*):\s(.*)", headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ",":
                value = value[:-1]
            sorted_headers[header] = value
        except IndexError:
            pass
    return sorted_headers


def heuristic(response, param_list):
    """Handle the heuristic of a response."""
    done = []
    forms = re.findall(r"(?i)(?s)<form.*?</form.*?>", response)
    for form in forms:
        method = re.search(r'(?i)method=[\'"](.*?)[\'"]', form)
        inputs = re.findall(r"(?i)(?s)<input.*?>", response)
        for inp in inputs:
            input_name = re.search(r'(?i)name=[\'"](.*?)[\'"]', inp)
            if input_name:
                input_type = re.search(r'(?i)type=[\'"](.*?)[\'"]', inp)
                input_value = re.search(r'(?i)value=[\'"](.*?)[\'"]', inp)
                input_name = decode_string(encode_string(input_name.group(1)))
                if input_name not in done:
                    if input_name in param_list:
                        param_list.remove(input_name)
                    done.append(input_name)
                    param_list.insert(0, input_name)
                    print(
                        "%s Heuristic found a potential parameter: %s%s%s"
                        % (good, green, input_name, end)
                    )
                    print("%s Prioritizing it" % good)


def extract_value(arrays, usable):
    """Extract the value from single valued list from a list of lists."""
    remaining_array = []
    for array in arrays:
        if len(array) == 1:
            usable.append(array[0])
        else:
            remaining_array.append(array)
    return remaining_array


def slicer(array, n=2):
    """Divide a list into n parts."""
    k, m = divmod(len(array), n)
    return list(
        array[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
        for i in range(n)
    )


def joiner(array, include):
    """Convert a list of parameters into parameter and value pair."""
    params = {}
    for element in array:
        params[element] = random_string(6)
    params.update(include)
    return params


def stabilize(url):
    """Pick up the best suiting protocol if not present already."""
    if "http" not in url:
        try:
            requests.get(
                "http://%s" % url
            )  # Makes request to the target with http schema
            url = "http://%s" % url
        except:  # if it fails, maybe the target uses https schema
            url = "https://%s" % url

    try:
        requests.get(url)  # Makes request to the target
    except Exception as e:  # if it fails, the target is unreachable
        if "ssl" in str(e).lower():
            pass
        else:
            print("%s Unable to connect to the target." % bad)
            quit()
    return url


def remove_tags(html):
    """Remove all the HTML from a web page source."""
    return re.sub(r"(?s)<.*?>", "", html)


def lineComparer(response1, response2):
    """Compare two webpage and find the non-matching lines."""
    response1 = response1.split("\n")
    response2 = response2.split("\n")
    num = 0
    dynamic_lines = []
    for line1, line2 in zip(response1, response2):
        if line1 != line2:
            dynamic_lines.append(num)
        num += 1
    return dynamic_lines


def random_string(n):
    """Generate a random string of length n."""
    return "".join(random.choice(string.ascii_lowercase) for entry in range(n))


def encode_string(string):
    """Encode a string to UTF."""
    return string.encode("utf-8")


def decode_string(string):
    """Decode a string from UTF to string."""
    return string.decode("utf-8")


def flatten_params(params):
    """Flatten the parameters."""
    flatted = []
    for name, value in params.items():
        flatted.append(name + "=" + value)
    return "?" + "&".join(flatted)


def get_params(data):
    """Retrieve parameters."""
    params = {}
    try:
        params = json.loads(str(data).replace("'", '"'))
        return params
    except json.decoder.JSONDecodeError:
        if data.startswith("?"):
            data = data[1:]
        parts = data.split("&")
        for part in parts:
            each = part.split("=")
            try:
                params[each[0]] = each[1]
            except IndexError:
                params = None
    return params
