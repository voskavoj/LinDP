## drop shortest
    idx = min(range(len(steps)), key=lambda i: steps[i].df.shape[0])
    dropped_steps.append(steps[idx])
    steps.pop(idx)
    no_of_steps -= 1
## /drop shortest

    average_step = compute_average_step(steps, True)
    old_average_step = average_step
    plot_average_step(steps, average_step, dropped_steps)

## start dropping by variation

    def rms_distance_to_average(df, df_avg):
        # Align on Time (inner join keeps only common timestamps)
        merged = df.merge(
            df_avg,
            on="Time",
            suffixes=("", "_avg"),
            how="inner"
        )

        # Compute squared distance at each time step
        sq_dist = (
                (merged["Roll"] - merged["Roll_avg"]) ** 2 +
                (merged["Pitch"] - merged["Pitch_avg"]) ** 2 +
                (merged["Yaw"] - merged["Yaw_avg"]) ** 2
        )

        # RMS distance
        return np.sqrt(sq_dist.mean())

    # JUST ONCE

    rms_values = [rms_distance_to_average(step.df, average_step.df) for step in steps]
    # print("rms_values", sorted(rms_values))

    KEPT_STEPS = min(10, len(rms_values))
    cutoff_rms = sorted(rms_values, reverse=True)[KEPT_STEPS - 1]

    kept_steps = []
    for i, step in enumerate(steps):
        if rms_values[i] < cutoff_rms:

            dropped_steps.append(step)
        else:
            kept_steps.append(step)

    no_of_steps = len(kept_steps)
    average_step = compute_average_step(kept_steps, True)

    plot_average_step(kept_steps, average_step, dropped_steps)

    ## REPEATEDLY
    average_step = old_average_step
    dropped_steps = list()
    no_of_steps = len(steps)
    while no_of_steps > 6:
        rms_values = [rms_distance_to_average(step.df, average_step.df) for step in steps]
        print("rms_values", sorted(rms_values))

        worst_rms_idx = rms_values.index(min(rms_values))
        print("worst_rms_idx", worst_rms_idx)
        dropped_steps.append(steps[worst_rms_idx])
        steps.pop(worst_rms_idx)
        no_of_steps -= 1
        print(no_of_steps, len(steps))
        average_step = compute_average_step(kept_steps, True)

    plot_average_step(steps, average_step)

## /start dropping by variation

