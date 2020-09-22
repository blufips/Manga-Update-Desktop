import json

settings_json = json.dumps([
    {'type': 'options',
     'title': 'Select a Server',
     'section': 'basicsettings',
     'key': 'Servers',
     'options': ['Manganelo', 'Mangareader']}])

if __name__ == '__main__':
    print(settings_json)
