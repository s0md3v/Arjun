import re

from core.utils import extract_js

def heuristic(response, paramList):
    found = []
    inputs = re.findall(r'(?i)<input.+?name=["\']?([^"\'\s>]+)', response)
    if inputs:
        for inpName in inputs:
            if inpName not in found:
                if inpName in paramList:
                    paramList.remove(inpName)
                found.append(inpName)
                paramList.insert(0, inpName)
    for script in extract_js(response):
        emptyJSvars = re.findall(r'([^\s!=<>]+)\s*=\s*[\'"`][\'"`]', response)
        if emptyJSvars:
            for var in emptyJSvars:
                if var not in found:
                    found.append(var)
                    if var in paramList:
                        paramList.remove(var)
                    paramList.insert(0, var)
        arrayJSnames = re.findall(r'([^\'"]+)[\'"]:\s?[\'"]', response)
        if arrayJSnames:
            for var in arrayJSnames:
                if var not in found:
                    found.append(var)
                    if var in paramList:
                        paramList.remove(var)
                    paramList.insert(0, var)
        return found
