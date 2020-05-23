from typing import List, Any, Callable, Set


def group(items: List[Any],
          grouping_func: Callable[[Any, Any], bool]) -> List[List[Any]]:
    result: List[List[Any]] = []

    ungrouped_index: Set[int] = set(range(len(items)))
    seen: Set[int] = set()
    while len(ungrouped_index) > 0:
        cur_idx = ungrouped_index.pop()
        cur_group: List[Any] = []
        group_candidate = {cur_idx}
        while len(group_candidate) > 0:
            cand_idx = group_candidate.pop()
            seen.add(cand_idx)
            cur_group.append(items[cand_idx])
            idx_nearby_of_cand = set(
                idx for idx in ungrouped_index if grouping_func(items[idx], items[cand_idx]) and idx not in seen)
            ungrouped_index.difference_update(idx_nearby_of_cand)
            group_candidate.update(idx_nearby_of_cand)

        result.append(cur_group)
    return result
