class HistoricalAdapter:
    def __init__(self, old_results, new_results, levels):
        self.__levels = levels
        self.__old_results = old_results
        self.__new_results = new_results

    def adapt(self):
        diffs = dict()
        max_diff = -1.0

        for table in self.__old_results.keys():
            if table in self.__new_results:
                diff = abs(self.__old_results[table] - self.__new_results[table])
                diffs[table] = diff
                max_diff = max(max_diff, diff)

        scaler = 0
        boosts = dict()

        if max_diff > 0.0 and self.__levels > 0:
            scaler = 1 / (max_diff * self.__levels)

        for table in diffs.keys():
            boost_fraction = diffs[table] * self.__levels * scaler
            priority_boost = round(self.__levels * boost_fraction)
            boosts[table] = priority_boost

        return boosts
