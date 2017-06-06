from time import strftime


class Logger:

    @staticmethod
    def log(message):
        """ writes the message into the *log_file.txt* and prints it to the stdout """
        current_date = strftime('%Y-%m-%d %H:%M:%S')
        with open('log_file.txt', 'a') as log_file:
            log_file.writelines([current_date + ': ' + message, '\n'])
        print(message)
