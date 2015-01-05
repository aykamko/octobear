import os, re
ignore_line = re.compile('\s*(#.*|\s*$)')

def parse_config(cfgfile):
    config = {}
    for line_no, line in enumerate(cfgfile.readlines()):
        if bool(ignore_line.match(line)): continue
        try:
            k, v = line.split()
            config[k] = v
        except Exception as e:
            print 'Error: line %d: %s' % (line_no, e)
    return config

config = parse_config(open(os.path.dirname(__file__) + '/config', 'r'))
