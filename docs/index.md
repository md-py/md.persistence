# Documentation

md.persistence component defines contracts to persist (save, read) python runtime data, 
and few useful tools out from box.

## Architecture overview

[![Architecture overview][architecture-overview]][architecture-overview]

## Component overview

```python3
GraphType = typing.Dict[str, typing.List[str]]  # filename -> [filename, ...]

def do_load(
    content: dict,
    import_list: typing.List[typing.Tuple[str, str]],
    filename: str,
    import_: ImportInterface,
) -> typing.Tuple[dict, GraphType]: ...
```

## Install

```sh
pip install md.persistence --index-url https://source.md.land/python/
```

## Usage
### Load configuration

`md.persistence.LoadInterface` component defines contract to load data 
from stream (file, socket, etc; typically, first). 

`load` method returns loaded content and graph of imports (it required for 
caching subsystem, optionally enabled on a higher level). 

Custom implementation may look like:

```python3
import typing
import md.persistence
import orjson


class Load(md.persistence.LoadInterface):  
    # naming things notice: reads as `domain.persistence.orjson.Load`
    def load(self, filename: str) -> typing.Tuple[typing.Any, md.persistence.GraphType]:
        with open(filename) as stream:
            content = orjson.loads(stream.read())
            assert isinstance(content)
            return content, {}

    def supports(self, filename: str) -> bool:
        return filename.endswith('.json')
```

Method `support` is required to test is loader may `load` content, it could be used 
along in service itself, but also in outside, for example:

```python
import typing
import md.persistence

def pick_loader_for(
    filename: str, 
    loader_list: typing.List[md.persistence.LoadInterface]
) -> typing.Union[md.persistence.LoadInterface, None]:
    for loader in loader_list:
        if loader.supports(filename=filename):
            return loader
    return None
```

### Import configuration

Modern configuration files may contain import statements right in file, for example:

```yaml
# /etc/container.yaml
!import parameters.yaml
!import services.yaml

parameters: ~
services: ~
```

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!-- /etc/container.xml -->
<container>
    <imports>
        <import resource="parameters.xml"/>
        <import resource="services.xml"/>
    </imports>
    
    <services/>
    <parameters/>
</container>
```

to handle such imports `md.persistence.LoadInterface` implementation 
may have optional `md.persistence.ImportInterface` dependency to call its 
`import_` method.

`md.persistence.ImportInterface` defines contract to handle import statement.

`md.persistence.DefaultImport` component provides default import implementation, 
based on recursion method: method `DefaultImport.import_` merges content 
and returns graph.


```json
{
  "imports": [
      "container/services.json",
      "container/parameters.json"
  ],
  "data": {
    "services": {},
    "parameters": {}
  }
}
```

```python3
import typing
import md.persistence
import orjson

class Load(md.persistence.LoadInterface):
    # naming things notice: reads as `domain.persistence.orjson.Load`
    def __init__(self, import_: md.persistence.ImportInterface) -> None:
        self._import = import_
        
    def load(self, filename: str) -> typing.Tuple[typing.Any, md.persistence.GraphType]:
        with open(filename) as stream:
            content = orjson.loads(stream.read())
            
        assert isinstance(content, dict)
        assert 'data' in content
        assert isinstance(content['data'])
        
        return md.persistence.do_load(
            filename=filename,
            content=content.get('data', {}),
            import_list=content.get('imports', []),
            import_=self._import,
        )

    def supports(self, filename: str) -> bool:
        return filename.endswith('.json')
```

### Dump configuration

`md.persistence.DumpInterface` defines contract to handle data dump into a stream (e.g. file),
for example:

```python3
import typing
import md.persistence
import orjson

class Dump(md.persistence.DumpInterface):
    # naming things notice: reads as `domain.persistence.orjson.Dump`
    def dump(self, filename: str, data: typing.Dict[str, typing.Dict]) -> None:
        with open(filename, 'wb') as stream:
            stream.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
```

### Responsibility desegregation

In most cases `load` and `dump` responsibilities are don't need to be 
joint into same class (due to [SRP principle][srp-principle]), but when it's required,
it may be designed like:

```python3
import md.persistence
import typing

class LoadAndDump(md.persistence.LoadInterface, md.persistence.DumpInterface):
    # naming things notice: reads as `domain.persistence.orjson.LoadAndDump`
    def load(self, filename: str) -> typing.Tuple[typing.Any, md.persistence.GraphType]: ...
    def supports(self, filename: str) -> bool: ...
    def dump(self, filename: str, data: typing.Dict[str, typing.Dict]) -> None:     ...
```

[architecture-overview]: _static/architecture-overview.class-diagram.svg
[srp-principle]: https://en.wikipedia.org/wiki/Single-responsibility_principle
