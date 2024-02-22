# TODO: Check for an off-by-1 error
# I'm not sure if this would create something odd

def find_component_idx_in_list(li: list, component: str, start_idx=0) -> int:
    """
    Given a list of components, finds given component, returns the index
    """
    if start_idx is None:
        start_idx = 0

    for idx, comp in enumerate(li):
        if comp.get("component") == component:
            if start_idx is None:
                return idx
            if idx >= start_idx:
                return idx
            
def find_component_seq_in_list(li: list, component: str, start_idx=0) -> int:
    """
    Given a list of components, finds given component, returns the sequence val
    """
    if start_idx is None:
        start_idx = 0

    for idx, comp in enumerate(li):
        if comp.get("component") == component:
            if start_idx is None:
                return comp.get("sequence")
            if idx >= start_idx:
                return comp.get("sequence")

