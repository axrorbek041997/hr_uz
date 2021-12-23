from functools import wraps

def exlude_redirect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        setattr(func, 'exlude_from_redirecting', True)
        print(func.__dir__(), func.__name__)
        return func(*args, **kwargs)
    return wrapper