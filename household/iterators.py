
class HouseholdStructureIterator:

    """Iterates household_structures for a household by survey_schedule.
    """

    def __init__(self, household=None):
        self.household_structures = list(
            household.householdstructure_set.all())
        self.household_structures.sort(
            key=lambda x: x.survey_schedule_object.start)
        self.n = 0

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        try:
            household_structure = self.household_structures[self.n]
        except (IndexError, TypeError):
            raise StopIteration
        self.n += 1
        return household_structure

    def __reversed__(self):
        return reversed(self.household_structures)

    def __len__(self):
        return len(self.household_structures)
