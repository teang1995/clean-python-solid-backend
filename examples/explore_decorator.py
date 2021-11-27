from functools import wraps


def test_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("decorated function")
        return f(*args, *kwargs)
    return decorated_function


@test_decorator
def func():
    print("calling func function")


if __name__ == "__main__":
    func()