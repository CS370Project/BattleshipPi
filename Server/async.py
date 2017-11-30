import threading
# Gives a framework for making asynchronous function calls
def asyncCall (functionCall, arguments):
    pthread = threading.Thread(target=functionCall, args=arguments)
    pthread.start()
    return