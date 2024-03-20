usage: fix2pipe++.py [-h] [-t TAGS] [-o] [-s {tag,name}]

fix2pipe++ fix parser

options:

  -h, --help            show this help message and exit
  
  -t TAGS, --tags TAGS  path to Tag.hpp (default: None)
  
  -o, --only-fix        only outputs formatted fix (default: False)

  -s {tag,name}, --sort-by {tag,name}
                        sorts fields by tag number or name (default: tag)


example:

kubectl logs mycontainer --tail=20000|fix2pipe++.py -t ~/Tag.hpp -s name
