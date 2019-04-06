import functools


def kwarg_result(name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            disable_kwarg_result = kwargs.pop('disable_kwarg_result', False)
            result = fn(*args, **kwargs)
            if disable_kwarg_result:
                return result
            else:
                return {name: result}
        return wrapper
    return decorator


def optional_kwarg_result(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        name = kwargs.pop('kwarg_result_name', None)
        result = fn(*args, **kwargs)
        if name is None:
            return result
        else:
            return {name: result}


def kwarg_inputs(fn):
    @functools.wraps(fn)
    def wrapper(arg, *args, **kwargs):
        if isinstance(arg, list):
            for result in arg:
                kwargs.update(result)
        return fn(*args, **kwargs)
    return wrapper
