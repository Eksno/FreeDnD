import json
data = {"this": {"has": True}, "barb": "bob"}


def add_field(var, val, raw_data):
    """Adds a value in the location var formatted as path-to-value to a dict"""
    
    data = raw_data.copy()
    fields = var.split("-")

    if len(fields) == 1:
        data[var] = val
        return data

    dict_fields = [data]
    for i, field in enumerate(fields):
        if i == len(fields) - 1:
            dict_fields[i][field] = val
            break

        try:
            dict_fields[i][field]
        except:
            dict_fields[i][field] = {}

        dict_fields.append(dict_fields[i][field])
    return data


data = add_field("this-is-a-test", True, data)
data = add_field("foo_bar", "bar", data)

print(json.dumps(data, indent=4))
for key in data:
    print(key)
