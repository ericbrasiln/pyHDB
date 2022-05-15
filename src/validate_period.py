'''Code for test an input string using regular expressions'''
import re

def validate_period(string):
    '''Function to validate the input period string using regular expressions'''
    if string == 'Todos':
        return True
    elif len(string)==11:
        pattern = r'^(17|18|19|20)\d0 - (17|18|19|20)\d9$'
        if re.match(pattern, string):
            if string[0:2] == string[7:9]:
                if string[2] == string[9]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False
        