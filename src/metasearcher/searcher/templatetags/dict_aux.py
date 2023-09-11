from django import template
import json

register = template.Library()

@register.simple_tag
def dictKeyLookup(dict, key):
    if type(dict) == str:
        dict = json.loads(s=dict)
    return dict.get(key, '')

@register.simple_tag
def transformLinks(dict):
    new_dict = {}
    for value in dict:
        if value.get('@_fa') == 'true':
            new_dict[value.get('@rel')] = value.get('@href')
    
    return new_dict

@register.simple_tag
def getAttribFromObjList(input_list, wanted_key, aux_wanted_key=None):
    """Returns the wanted key from the first element of the list 
    provided only if it contains the value on the conditional key.
    If not, it returns None
    """
    if type(input_list) == list:
        for obj in input_list:
            if aux_wanted_key != None:
                result = obj[wanted_key][aux_wanted_key]
            else:
                result = obj[wanted_key]

            if type(result) == list:
                new_result = ''
                for part in result:
                    new_result = new_result + part
                return new_result
            return result
    return None


@register.simple_tag
def getAttribFromObjListIf(input_list, wanted_key, conditional_key, value):
    """Returns the wanted key from the first element of the list 
    provided only if it contains the value on the conditional key.
    If not, it returns None
    """
    if type(input_list) == list:
        for obj in input_list:
            if obj[conditional_key] == value:
                return obj[wanted_key]            
    return None

@register.simple_tag
def summOnTemplate(val1, val2):
    if type(val1) != type(val2) and type(val1) != int:
        return None
    return val1 + val2