class RentComparator:
    """Rent comparison service (deferred).

    The interface is defined now so it can be added later without changing
    the rest of the app. It would compare the advertised rent with the RTB
    average for the area.
    """

    def compare(self, rent, area):
        raise NotImplementedError("Rent comparison is deferred to a later version")