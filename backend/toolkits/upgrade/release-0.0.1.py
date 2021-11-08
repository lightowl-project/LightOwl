from .upgrade import Upgrade


class Release001(Upgrade):
    def __init__(self):
        super().__init__(self)


    def upgrade(self):
        pass


if __name__ == "__main__":
    release = Release001()
    release.upgrade()
