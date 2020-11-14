import time;
from datetime import datetime;


def time_function(function, *args, n=10000, **kwargs):
    """ time how long it takes for a function to evaluate n times """
    initial_time = time.time();
    for _ in range(n):
        function(*args, **kwargs);
    final_time = time.time();
    return final_time - initial_time;

def record(details):
    """ record a performance test """
    string = "<{}>\n\tDate and time of test: {}\n\tTotal time: {}\n\tTotal updates: {}\n\tAverage update time: {}\n\n";
    with open("performance_tests.txt", "a") as file:
        file.write(string.format(details["description"], datetime.now(), details["total time"],
                                 details["total updates"], details["average update time"]));
