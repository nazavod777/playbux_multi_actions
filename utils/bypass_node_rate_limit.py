import requests.exceptions


def bypass_ratelimit(current_function,
                     **kwargs) -> any:
    try:
        return current_function(**kwargs)

    except (requests.exceptions.Timeout, TimeoutError, requests.exceptions.ConnectionError):
        return bypass_ratelimit(current_function=current_function,
                                **kwargs)

    except requests.exceptions.HTTPError as error:
        if '[429]' in str(error.response) or '[502]' in str(error.response):
            return bypass_ratelimit(current_function=current_function,
                                    **kwargs)

        raise error

    except Exception as error:
        if not str(error):
            return bypass_ratelimit(current_function=current_function,
                                    **kwargs)

        raise error
