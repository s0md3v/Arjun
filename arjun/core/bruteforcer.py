"""The brute forcer of Arjun."""
from arjun.core.requester import requester
from arjun.core.utils import joiner, random_string, remove_tags


def quick_brute_force(
    params,
    original_response,
    original_code,
    reflections,
    factors,
    include,
    delay,
    headers,
    url,
    get,
    variables,
):
    """Quick brute forcer."""
    merged_parameters = joiner(params, include)
    new_response = requester(
        url, merged_parameters, headers, get, delay, variables
    )
    if new_response.status_code != original_code:
        return params
    elif factors['same_html'] and len(new_response.text) != (
        len(original_response)
    ):
        return params
    elif factors['same_plain_text'] and len(
        remove_tags(original_response)
    ) != len(remove_tags(new_response.text)):
        return params
    elif True:
        for param, value in merged_parameters.items():
            if (
                param not in include
                and new_response.text.count(value) != reflections
            ):
                return params
    else:
        return False


def brute_force(
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
):
    """Standard brute forcer."""
    fuzz = random_string(6)
    data = {param: fuzz}
    data.update(include)
    response = requester(url, data, headers, get, delay, variables)
    new_reflections = response.text.count(fuzz)
    reason = False
    if response.status_code != original_code:
        reason = 'Different response code'
    elif reflections != new_reflections:
        reason = 'Different number of reflections'
    elif factors['same_html'] and len(response.text) != (
        len(original_response)
    ):
        reason = 'Different content length'
    elif factors['same_plain_text'] and len(remove_tags(response.text)) != (
        len(remove_tags(original_response))
    ):
        reason = 'Different plain-text content length'
    if reason:
        return {param: reason}
    else:
        return None
