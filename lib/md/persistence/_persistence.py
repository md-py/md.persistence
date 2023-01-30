import typing
import os

import md.python.dict


# Metadata
__author__ = 'https://md.land/md'
__version__ = '0.2.0'
__all__ = (
    # Metadata
    '__author__',
    '__version__',
    # Contract
    'GraphType',
    'LoadInterface',
    'DumpInterface',
    'ImportInterface',
    # Exception
    'PersistenceExceptionInterface',
    'LoadException',
    'DumpException',
    'ImportException',
    # Implementation
    'DefaultImport',
    'do_load'
)

# Contract
GraphType = typing.Dict[str, typing.List[str]]  # filename -> [filename, ...]


class LoadInterface:
    def load(self, filename: str) -> typing.Tuple[typing.Any, GraphType]:
        raise NotImplementedError

    def supports(self, filename: str) -> bool:
        raise NotImplementedError


class DumpInterface:
    def dump(self, filename: str, data: typing.Any) -> None:
        raise NotImplementedError


class ImportInterface:
    def import_(
        self,
        content: dict,
        resource_list: typing.List[typing.Tuple[str, str]]
    ) -> typing.Tuple[dict, GraphType]:
        raise NotImplementedError


# Exception
class PersistenceExceptionInterface:
    pass


class LoadException(RuntimeError, PersistenceExceptionInterface):
    IMPORT_ERROR = 1
    PARSE_ERROR = 2
    NOT_SUPPORTED = 3
    REQUIREMENT_MISSED = 4

    def __init__(self, code: int = 0, path: str = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code = code
        self.path = path

    @classmethod
    def as_import_error(cls, path: str = None, *args, **kwargs) -> 'LoadException':
        return cls(code=cls.IMPORT_ERROR, path=path, *args, **kwargs)

    @classmethod
    def as_parse_error(cls, path: str = None, *args, **kwargs) -> 'LoadException':
        return cls(code=cls.PARSE_ERROR, path=path, *args, **kwargs)

    @classmethod
    def as_not_supported(cls, path: str = None, *args, **kwargs) -> 'LoadException':
        return cls(code=cls.NOT_SUPPORTED, path=path, *args, **kwargs)

    @classmethod
    def as_requirement_missed(cls, path: str = None, *args, **kwargs) -> 'LoadException':
        return cls(code=cls.REQUIREMENT_MISSED, path=path, *args, **kwargs)


class DumpException(RuntimeError, PersistenceExceptionInterface):
    def __init__(self, code: int = 0, path: str = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code = code
        self.path = path


class ImportException(RuntimeError, PersistenceExceptionInterface):
    NOT_EXISTS = 1
    MERGE_ERROR = 2
    RECURSION_ERROR = 3

    def __init__(self, code: int = 0, path: str = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code = code
        self.path = path

    @classmethod
    def as_not_exists(cls, path: str = None, *args, **kwargs) -> 'ImportException':
        return cls(code=cls.NOT_EXISTS, path=path, *args, **kwargs)

    @classmethod
    def as_merge(cls, path: str = None, *args, **kwargs) -> 'ImportException':
        return cls(code=cls.MERGE_ERROR, path=path, *args, **kwargs)

    @classmethod
    def as_recursion_error(cls, path: str = None, *args, **kwargs) -> 'ImportException':
        return cls(code=cls.RECURSION_ERROR, path=path, *args, **kwargs)


# Implementation
class DefaultImport(ImportInterface):  # Warning: instance is not thread safe
    def __init__(self, load: LoadInterface, merge_dictionary: md.python.dict.MergeDictionaryInterface) -> None:
        self._load = load
        self._merge_dictionary = merge_dictionary

    def import_(
        self,
        content: dict,
        resource_list: typing.List[typing.Tuple[str, str]],
    ) -> typing.Tuple[typing.Dict, GraphType]:
        file_graph: GraphType = {}
        for resource_type, resource_path in resource_list:
            if resource_type == 'directory':
                raise NotImplementedError('Directory import is not implemented yet')

            try:
                resource_content, nested_file_graph = self._load.load(filename=resource_path)
            except FileNotFoundError as e:
                raise ImportException.as_not_exists(
                    f'Unable to import `{resource_path!s}`, file not exists',
                    path=resource_path
                ) from e

            if not isinstance(resource_content, dict):
                raise ImportException.as_merge(
                    'Unable to merge configuration, `dict` type expected, '
                    f'`{type(resource_content)!s}` got, in `{resource_path!s}`',
                    path=resource_path
                )

            file_graph = {**file_graph, **nested_file_graph}  # keys must not intersect, so there is default merge
            content = self._merge_dictionary.merge(left=resource_content, right=content)
        return content, file_graph


def do_load(
    content: dict,
    import_list: typing.List[typing.Tuple[str, str]],
    filename: str,
    import_: ImportInterface,
) -> typing.Tuple[dict, GraphType]:
    file_graph: GraphType = {filename: []}

    # transform import list
    filename_dir = os.path.dirname(filename)
    for index, (import_type, import_filename) in enumerate(import_list):
        assert import_type in ('file', 'directory')

        resource_path = os.path.join(filename_dir, import_filename)
        resource_path = os.path.abspath(resource_path)

        assert (
            (import_type == 'file' and os.path.isfile(resource_path)) or
            (import_type == 'directory' and os.path.isdir(resource_path))
        )

        import_list[index] = (import_type, resource_path)
        file_graph[filename].append(resource_path)

    # perform import
    if len(import_list) > 0:
        try:
            content, nested_file_graph = import_.import_(content=content, resource_list=import_list)
        except ImportException as import_exception:
            raise LoadException.as_import_error(
                f'Unable to load `{filename!s}` as unable to perform import `{import_exception.path}`',
                path=import_exception.path
            ) from import_exception

        assert isinstance(content, dict)
        file_graph = {**file_graph, **nested_file_graph}
    return content, file_graph
