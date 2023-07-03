from typing import Dict, List, Optional, Set

Children = List['Person']


class Person:

    def __init__(self, pid: int, name: str,
                 birth_year: int, parent: Optional['Person'],
                 children: Children):
        self.pid = pid
        self.name = name
        self.birth_year = birth_year
        self.parent: Optional['Person'] = parent
        self.children: Children = children

    def is_valid(self) -> bool:
        valid: Set[bool] = set()
        Person.is_valid_rec(self, 0, valid)
        return len(valid) == 0

    def is_valid_rec(self, birth_year: int, valid: Set[bool]) -> None:
        if self.name == "":
            valid.add(False)
            return

        if birth_year >= self.birth_year:
            valid.add(False)
            return

        names: Set[str] = set()
        for child in self.children:
            if child.name in names:
                valid.add(False)
                return
            names.add(child.name)

        for child in self.children:
            Person.is_valid_rec(child, self.birth_year, valid)

    def draw(self, names_only: bool) -> None:
        fathers = 0
        fathers_index = [0]
        Person.draw_rec(self, names_only, fathers, fathers_index)

    def draw_rec(self, names_only: bool, fathers: int,
                 fathers_index: List[int]) -> None:
        for i in range(fathers):
            assert self.parent is not None
            if i in fathers_index:
                if self.parent.children[-1] == self and i == fathers - 1:
                    fathers_index.pop()
                    print("└─ ", end="")
                elif i == fathers - 1:
                    print("├─ ", end="")
                else:
                    print("│  ", end="")
            else:
                print("   ", end="")
        if names_only:
            print(self.name)
        else:
            print(self.name,
                  "(" + str(self.birth_year) + ")",
                  "[" + str(self.pid) + "]")
        for child in self.children:
            if fathers not in fathers_index:
                fathers_index.append(fathers)
            Person.draw_rec(child, names_only, fathers + 1, fathers_index)

    def parents_younger_than(self, age_limit: int) -> Set[int]:
        parents: Set[int] = set()
        Person.parents_younger_or_older_than_rec(self, age_limit,
                                                 True, parents)
        return parents

    def parents_older_than(self, age_limit: int) -> Set[int]:
        parents: Set[int] = set()
        Person.parents_younger_or_older_than_rec(self, age_limit,
                                                 False, parents)
        return parents

    def parents_younger_or_older_than_rec(self, age_limit: int, older: bool,
                                          parents: Set[int]) -> None:
        for child in self.children:
            if older:
                if child.birth_year - self.birth_year < age_limit:
                    parents.add(self.pid)
            else:
                if child.birth_year - self.birth_year > age_limit:
                    parents.add(self.pid)
            Person.parents_younger_or_older_than_rec(child, age_limit,
                                                     older, parents)

    def childless(self) -> Set[int]:
        without_kids: Set[int] = set()
        Person.childless_rec(self, without_kids)
        return without_kids

    def childless_rec(self, without_kids: Set[int]) -> None:
        if not self.children:
            without_kids.add(self.pid)
        for child in self.children:
            Person.childless_rec(child, without_kids)

    def ancestors(self) -> List['Person']:
        ancestors_list: List[Person] = list()
        parent = self.parent
        while parent is not None:
            ancestors_list.append(parent)
            parent = parent.parent
        ancestors_list.reverse()
        return ancestors_list

    def order_of_succession(self, alive: Set[int]) -> Dict[int, int]:
        succesion_order = Person.order_of_succession_rec(self, alive)
        succesion = []
        for successor in succesion_order:
            if successor.pid in alive:
                succesion.append(successor)
        order = {}
        for i, successor in enumerate(succesion):
            order[successor.pid] = i + 1
        return order

    def order_of_succession_rec(self, alive: Set[int]) -> List['Person']:
        children: List['Person'] = []
        for child in self.children:
            children.append(child)
        if children:
            children.sort(key=lambda x: x.birth_year)
        order = []
        for child in children:
            order.append(child)
            order += Person.order_of_succession_rec(child, alive)
        return order

    def remove_extinct_branches(self, alive: Set[int]) -> None:
        Person.remove_extinct_branches_rec(self, alive, self)

    def remove_extinct_branches_rec(self, alive: Set[int],
                                    parent: 'Person') -> None:
        for i in range(len(self.children) - 1, -1, -1):
            Person.remove_extinct_branches_rec(self.children[i], alive, parent)

        if not self.children:
            if self.pid not in alive and \
                    self.parent is not None and self != parent:
                self.parent.children.remove(self)


def build_family_tree(names: Dict[int, str],
                      children: Dict[int, List[int]],
                      birth_years: Dict[int, int]) -> Optional[Person]:
    names_set = set()
    birth_years_set = set()
    children_set = set()

    for pid in names:
        names_set.add(pid)
    parent_set = names_set.copy()

    for pid in birth_years:
        if pid not in names_set:
            return None
        birth_years_set.add(pid)

    for pid in children:
        if pid not in names_set:
            return None
        for child in children[pid]:
            if child in children_set:
                return None
            if child not in names_set:
                return None
            children_set.add(child)
            parent_set.remove(child)

    if names_set != birth_years_set:
        return None

    if len(parent_set) != 1:
        return None

    return build_family(names, children, birth_years,
                        None, list(parent_set)[0])


def build_family(names: Dict[int, str],
                 children: Dict[int, List[int]],
                 birth_years: Dict[int, int],
                 parent: Optional[Person], parent_pid: int) -> Person:
    person = Person(parent_pid, names[parent_pid],
                    birth_years[parent_pid], parent, [])

    if parent_pid in children:
        for child in children[parent_pid]:
            person.children.append(build_family(names, children,
                                                birth_years, person, child))

    return person


def valid_family_tree(person: Person) -> bool:
    while person.parent is not None:
        person = person.parent
    return Person.is_valid(person)


def test_one_person() -> None:
    adam = build_family_tree({1: "Adam"}, {}, {1: 1})
    assert isinstance(adam, Person)
    assert adam.pid == 1
    assert adam.birth_year == 1
    assert adam.name == "Adam"
    assert adam.children == []
    assert adam.parent is None

    assert adam.is_valid()
    assert adam.parents_younger_than(18) == set()
    assert adam.parents_older_than(81) == set()
    assert adam.childless() == {1}
    assert adam.ancestors() == []
    assert adam.order_of_succession({1}) == {}


def example_family_tree() -> Person:

    qempa = build_family_tree(
        {
            17: "Qempa'",
            127: "Thok Mak",
            290: "Worf",
            390: "Worf",
            490: "Mogh",
            590: "Kurn",
            611: "Ag'ax",
            561: "K'alaga",
            702: "Samtoq",
            898: "K'Dhan",
            429: "Grehka",
            1000: "Alexander Rozhenko",
            253: "D'Vak",
            106: "Elumen",
            101: "Ga'ga",
        },
        {
            17: [127, 290],
            390: [898, 1000],
            1000: [253],
            127: [611, 561, 702],
            590: [429, 106, 101],
            490: [390, 590],
            290: [490],
            702: [],
        },
        {
            1000: 2366,
            101: 2366,
            106: 2357,
            127: 2281,
            17: 2256,
            253: 2390,
            290: 2290,
            390: 2340,
            429: 2359,
            490: 2310,
            561: 2302,
            590: 2345,
            611: 2317,
            702: 2317,
            898: 2388,
        }
    )

    assert qempa is not None
    return qempa


def test_example() -> None:
    qempa = example_family_tree()
    assert qempa.name == "Qempa'"
    assert qempa.pid == 17
    assert qempa.birth_year == 2256
    assert qempa.parent is None
    assert len(qempa.children) == 2

    thok_mak, worf1 = qempa.children
    assert worf1.name == "Worf"
    assert worf1.pid == 290
    assert worf1.birth_year == 2290
    assert worf1.parent == qempa
    assert len(worf1.children) == 1

    mogh = worf1.children[0]
    assert mogh.name == "Mogh"
    assert mogh.pid == 490
    assert mogh.birth_year == 2310
    assert mogh.parent == worf1
    assert len(mogh.children) == 2

    worf2 = mogh.children[0]
    assert worf2.name == "Worf"
    assert worf2.pid == 390
    assert worf2.birth_year == 2340
    assert worf2.parent == mogh
    assert len(worf2.children) == 2

    alex = worf2.children[1]
    assert alex.name == "Alexander Rozhenko"
    assert alex.pid == 1000
    assert alex.birth_year == 2366
    assert alex.parent == worf2
    assert len(alex.children) == 1

    assert qempa.is_valid()
    assert alex.is_valid()
    assert valid_family_tree(qempa)
    assert valid_family_tree(alex)

    thok_mak.name = ""
    assert not qempa.is_valid()
    assert alex.is_valid()
    assert not valid_family_tree(qempa)
    assert not valid_family_tree(alex)
    thok_mak.name = "Thok Mak"

    thok_mak.birth_year = 2302
    assert not qempa.is_valid()
    assert alex.is_valid()
    assert not valid_family_tree(qempa)
    assert not valid_family_tree(alex)
    thok_mak.birth_year = 2281

    assert qempa.parents_younger_than(12) == set()
    assert qempa.parents_younger_than(15) == {590}
    assert qempa.parents_younger_than(21) == {290, 590}

    assert qempa.parents_older_than(48) == set()
    assert qempa.parents_older_than(40) == {390}

    assert thok_mak.parents_younger_than(21) == set()
    assert thok_mak.parents_older_than(40) == set()

    assert qempa.childless() == {101, 106, 253, 429, 561, 611, 702, 898}
    assert thok_mak.childless() == {611, 561, 702}
    assert alex.ancestors() == [qempa, worf1, mogh, worf2]
    assert thok_mak.ancestors() == [qempa]
    assert qempa.ancestors() == []

    alive = {17, 101, 106, 127, 253, 290, 390, 429,
             490, 561, 590, 611, 702, 898, 1000}

    succession = {
        101: 14,
        106: 12,
        127: 1,
        253: 9,
        290: 5,
        390: 7,
        429: 13,
        490: 6,
        561: 2,
        590: 11,
        611: 3,
        702: 4,
        898: 10,
        1000: 8,
    }

    assert qempa.order_of_succession(alive) == succession

    alive.remove(17)
    assert qempa.order_of_succession(alive) == succession

    alive -= {127, 290, 490, 590}

    assert qempa.order_of_succession(alive) == {
        561: 1,
        611: 2,
        702: 3,
        390: 4,
        1000: 5,
        253: 6,
        898: 7,
        106: 8,
        429: 9,
        101: 10,
    }

    assert mogh.order_of_succession(alive) == {
        390: 1,
        1000: 2,
        253: 3,
        898: 4,
        106: 5,
        429: 6,
        101: 7,
    }


def draw_example() -> None:
    qempa = example_family_tree()
    print("První příklad:")
    qempa.draw(False)

    print("\nDruhý příklad:")
    qempa.children[1].children[0].draw(False)

    alive1 = {101, 106, 253, 429, 561, 611, 702, 898}
    alive2 = {101, 106, 253, 390, 898, 1000}
    for alive in alive1, alive2:
        print(f"\nRodokmen po zavolání remove_extinct_branches({alive})\n"
              "na výchozí osobě:")
        qempa = example_family_tree()
        qempa.remove_extinct_branches(alive)
        qempa.draw(False)

    print(f"\nRodokmen po zavolání remove_extinct_branches({alive})\n"
          "na osobě jménem Mogh:")
    qempa = example_family_tree()
    qempa.children[1].children[0].remove_extinct_branches(alive2)
    qempa.draw(False)


if __name__ == '__main__':
    test_one_person()
    test_example()
    # draw_example()  # uncomment to run
