# Notice: holder class for setting variable in if statement
# helpful for code climate code complexity to respect
class Holder(object):
    def set(self, value):
        self.value = value
        return value

    def get(self):
        return self.value
