def generate_grid_connections(rows, cols):
    """
    Generates PDDL 'connected' predicates for an N x M grid.

    Args:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.

    Returns:
        str: A string containing all the PDDL 'connected' predicates.
    """
    connections = []
    for r in range(rows):
        for c in range(cols):
            current_loc = f"loc-{r}-{c}"

            # Connect to the right (East)
            if c + 1 < cols:
                right_loc = f"loc-{r}-{c+1}"
                connections.append(f"(connected {current_loc} {right_loc})")
                connections.append(f"(connected {right_loc} {current_loc})") # Bidirectional

            # Connect downwards (South)
            if r + 1 < rows:
                down_loc = f"loc-{r+1}-{c}"
                connections.append(f"(connected {current_loc} {down_loc})")
                connections.append(f"(connected {down_loc} {current_loc})") # Bidirectional

    return "\n".join(sorted(list(set(connections))))

if __name__ == "__main__":
    grid_rows = 8
    grid_cols = 8
    pddl_connections = generate_grid_connections(grid_rows, grid_cols)

    print(f";; Generated connections for a {grid_rows}x{grid_cols} grid")
    print(pddl_connections)

    # You can also save this to a file
    # with open("generated_connections.pddl", "w") as f:
    #     f.write(pddl_connections)
