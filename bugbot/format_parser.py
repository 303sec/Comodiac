import re
import math
import re
from urllib.parse import urlparse

def format_parser(in_data, out_format):
    # removes and splits by any non-alphanumeric characters. If there are multiple symbols it creates whitespace, hence the filter.
    # in_format is a string like scheme://host:port, which we need to turn into an array of parts
    # in_format_items = list(filter(None, re.split('[^a-zA-Z]', in_format)))
    out_format_items = list(filter(None, re.split('[^a-zA-Z]', out_format)))
    out_data_dict = {}
    # Should be something like ['scheme', 'host', 'port']. Note that this is probably not the best way to do this!
    # We want to check that there's nothing required in outformat that isn't in the in_data.
    in_data_parsed = urlparse(in_data)
    in_data_dict = {'scheme': in_data_parsed.scheme, 'host': in_data_parsed.hostname, 'port': in_data_parsed.port,\
    'path': in_data_parsed.path, 'query': in_data_parsed.query, 'fragment': in_data_parsed.fragment}
    # Good old url parse. Gets us the relevant parts
    # returns data parsed for output. Coverts the in_data to out_data
    # ParseResult(scheme='https', netloc='www.google.com', path='', params='', query='', fragment='')
    for key, data in in_data_dict.items():
        if key in out_format_items:
            if data:
                out_data_dict[key] = in_data_dict[key]
            else:
                print('Error! in / out data format mismatch')
                return (-1, key)

    # Need to get a bit hacky to make some stuff work
    if 'scheme' in out_data_dict:
        out_data_dict['scheme'] = out_data_dict['scheme'] + '://'

    if 'port' in out_data_dict:
        out_data_dict['port'] = ':' + str(out_data_dict['port'])

    if 'query' in out_data_dict:
        out_data_dict['query'] = '?' + out_data_dict['query']

    if 'fragment' in out_data_dict:
        out_data_dict['fragment'] = '#' + out_data_dict['fragment']

    out_list = [y for x, y in out_data_dict.items()]
    join_hack = ''
    return join_hack.join(out_list)


print('\nShould return -1 as no port in data')
print(format_parser('https://google.com/test', 'scheme://host:port/path'))

print('\nOutput should be https://google.com')
print(format_parser('https://google.com/test', 'scheme://host'))

print('\nOutput should be google.com')
print(format_parser('https://google.com:8080/test?this=that#asdr', 'host'))

print('\nOutput should be /testing/this/bit')
print(format_parser('https://google.com:8080/testing/this/bit?this=that#asdr', 'path'))

print('\nOutput should be https://google.com:8080/testing/this/bit?this=that#asdr')
print(format_parser('https://google.com:8080/testing/this/bit?this=that#asdr', 'scheme://host:port/path?query#fragment'))