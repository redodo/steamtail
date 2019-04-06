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


def kwarg_inputs(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (list, tuple)):
                remove_from_arg = []
                for result in arg:
                    if isinstance(result, dict):
                        kwargs.update(result)
                        remove_from_arg.append(result)
                for result in remove_from_arg:
                    arg.remove(result)
        args = [arg for arg in args if arg]
        return fn(*args, *kwargs)
