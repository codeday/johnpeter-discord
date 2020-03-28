class RandomFuncs(object):
    @staticmethod
    def paginate(string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))
