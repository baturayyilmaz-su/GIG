import subprocess
import multiprocessing
from abc import ABC, abstractmethod


class CommandExecutor(ABC):
    def __init__(self):
        self.TIMEOUT_VALUE = 200  # in seconds

    def timeout(self, func, command, timeoutValue):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        process = multiprocessing.Process(target=func, args=[command, return_dict])
        process.start()
        process.join(timeout=timeoutValue)

        if process.is_alive():  # TIMEOUT VALUE IS REACHED AND PROCESS IS STILL WORKING
            process.terminate()
            return False
        else:  # PROCESS IS FINISHED
            return return_dict.values()[0]

    def runProcess(self, command, return_dict):
        subPro = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return_dict[0] = subPro

    @abstractmethod
    def _getCommandString(self):
        pass

    def runCommand(self):
        command = self._getCommandString()

        subPro = self.timeout(func=self.runProcess, command=command, timeoutValue=self.TIMEOUT_VALUE)
        if subPro is False:  # then the process terminated because timeout is being reached
            return None
        # Process is finished. subPro has a value (which has the stdout of the process)
        else:
            processOutput = subPro.stdout.decode('utf-8')
            return processOutput
