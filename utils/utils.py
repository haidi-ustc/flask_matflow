import os
import sys
import logging
import shutil
import hashlib
import numpy as np
from enum import Enum
from pydantic import BaseModel
from typing import List, Union, Dict, Optional, Any
from monty.json import MSONable
import bson

def hash_text(text: Union [str, dict], method="sha256") -> str:

    if isinstance(text,dict):
       text = str(text)
    if method=="sha256":
       m = hashlib.sha256()
    else:
       m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def create_path (path,back=False) :
    if  path[-1] != "/":
        path += '/'
    if os.path.isdir(path) :
        if back:
           dirname = os.path.dirname(path)
           counter = 0
           while True :
               bk_dirname = dirname + ".bk%03d" % counter
               if not os.path.isdir(bk_dirname) :
                   shutil.move (dirname, bk_dirname)
                   break
               counter += 1
           os.makedirs (path)
           return path
        else:
           return path
    os.makedirs (path)
    return path

class ChangeDirectory:
    def __init__(self, path):
        self.path = path
        self.original_path = None

    def __enter__(self):
        self.original_path = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.original_path)

def load_class(modulepath, classname):
    """
    Load and return the class from the given module.

    Args:
        modulepath (str): dotted path to the module. eg: "pymatgen.io.vasp.sets"
        classname (str): name of the class to be loaded.

    Returns:
        class
    """
    mod = __import__(modulepath, globals(), locals(), [classname], 0)
    return getattr(mod, classname)


def get_logger(
    name,
    level=logging.DEBUG,
    log_format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(log_format)
    sh = logging.StreamHandler(stream=stream)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def jsanitize(obj, strict=False, allow_bson=False):
    """
    This method cleans an input json-like object, either a list or a dict or
    some sequence, nested or otherwise, by converting all non-string
    dictionary keys (such as int and float) to strings, and also recursively
    encodes all objects using Monty's as_dict() protocol.
    Args:
        obj: input json-like object.
        strict (bool): This parameters sets the behavior when jsanitize
            encounters an object it does not understand. If strict is True,
            jsanitize will try to get the as_dict() attribute of the object. If
            no such attribute is found, an attribute error will be thrown. If
            strict is False, jsanitize will simply call str(object) to convert
            the object to a string representation.
        allow_bson (bool): This parameters sets the behavior when jsanitize
            encounters an bson supported type such as objectid and datetime. If
            True, such bson types will be ignored, allowing for proper
            insertion into MongoDb databases.
    Returns:
        Sanitized dict that can be json serialized.
    """
    if allow_bson and (
        isinstance(obj, (datetime.datetime, bytes))
        or (bson is not None and isinstance(obj, bson.objectid.ObjectId))
    ):
        return obj
    if isinstance(obj, (list, tuple, set)):
        return [jsanitize(i, strict=strict, allow_bson=allow_bson) for i in obj]
    if np is not None and isinstance(obj, np.ndarray):
        return [
            jsanitize(i, strict=strict, allow_bson=allow_bson) for i in obj.tolist()
        ]
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, dict):
        return {
            k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
            for k, v in obj.items()
        }
    if isinstance(obj, MSONable):
        return {
            k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
            for k, v in obj.as_dict().items()
        }

    if isinstance(obj, BaseModel):
        return {
            k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
            for k, v in obj.dict().items()
        }
    if isinstance(obj, (int, float)):
        if np.isnan(obj):
            return 0
        return obj

    if obj is None:
        return None

    if not strict:
        return obj.__str__()

    if isinstance(obj, str):
        return obj.__str__()

    return jsanitize(obj.as_dict(), strict=strict, allow_bson=allow_bson)

if __name__=="__main__":
   print(jsanitize([]))
   print(jsanitize({"a":[1]}))
