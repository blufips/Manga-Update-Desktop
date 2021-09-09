import json

settings_json = json.dumps([
    {'type': 'options',
     'title': 'Select a Server',
     'section': 'basicsettings',
     'key': 'Servers',
     'options': ['Mangahub']},
     {'type': 'bool',
      'title': 'Dark Mode',
      'section': 'basicsettings',
      'key': 'darkmode'
     },
     {'type': 'options',
     'title': 'Version Number',
     'section': 'basicsettings',
     'key': 'Version'}])

if __name__ == '__main__':
    print(settings_json)
