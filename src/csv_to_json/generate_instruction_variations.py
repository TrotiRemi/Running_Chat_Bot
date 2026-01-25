def generate_instruction_variations(week_num, total_weeks, goal, level, training_days, age=None):
    instructions = []

    format_hint = (
        "Format attendu: 7 lignes, une par jour, "
        "de Lundi à Dimanche, au format 'Jour: Activité'."
    )

    instr1 = (
        f"Generate a complete week ({week_num}) of a {total_weeks}-week "
        f"{goal} running program. Training level: {level}, "
        f"{training_days} training days per week"
    )
    instr1 += f". {format_hint}"
    instructions.append(instr1)

    instr2 = (
        f"Create the weekly training schedule for week {week_num} "
        f"({week_num}/{total_weeks}) of a {level} {goal} program. "
        f"{training_days} workouts per week. {format_hint}"
    )
    instructions.append(instr2)

    instr3 = (
        f"Provide a {level} running schedule for week {week_num} "
        f"of {total_weeks} weeks targeting {goal}. "
        f"{training_days} training sessions needed. {format_hint}"
    )
    instructions.append(instr3)

    progression_pct = int((week_num / total_weeks) * 100)
    instr4 = (
        f"At {progression_pct}% through a {total_weeks}-week {goal} program ({level}), "
        f"generate week {week_num} with {training_days} training days. {format_hint}"
    )
    instructions.append(instr4)

    return instructions
