from dataclasses import dataclass, field

from crypto.utils.model import Model


@dataclass
class ProfileModel(Model):
    _id: int
    name: str
    money: int
    cryptocoins: int
    miner: dict[str, int] = field(default_factory=dict)
