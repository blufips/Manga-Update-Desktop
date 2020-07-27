import json

settings_json = json.dumps([
    {'type': 'options',
     'title': 'Select a Server',
     'section': 'basicsettings',
     'key': 'Servers',
     'options': ['Manganelo']}])

if __name__ == '__main__':
    print(settings_json)
