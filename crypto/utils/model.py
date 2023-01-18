from dataclasses import asdict, dataclass


@dataclass
class Model:
    @property
    def __dict__(self) -> dict:
        return asdict(self)

    @property
    def json(self) -> dict:
        return self.__dict__
